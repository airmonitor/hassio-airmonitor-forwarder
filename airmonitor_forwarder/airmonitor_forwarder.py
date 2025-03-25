import json
import time
import logging
import requests
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s]:%(name)s:%(message)s")
logger = logging.getLogger("AirMonitor-Forwarder")
print("\nAll environment variables (one per line):")
for key, value in os.environ.items():
    print(f"{key}={value}")

# Configuration from environment variables
AIRMONITOR_API_URL = "https://airmonitor.pl/prod/measurements"
# Get environment variables with validation
try:
    HA_TOKEN = os.environ["HA_TOKEN"]
    HA_URL = os.environ["HA_URL"]
    AIRMONITOR_API_KEY = os.environ["AIRMONITOR_API_KEY"]
    LAT = os.environ["LAT"]
    LONG = os.environ["LONG"]
    SENSOR_MODEL = os.environ["SENSOR_MODEL"]
        
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    sys.exit(1)

# Define which Home Assistant entities to forward
ENTITIES_TO_FORWARD = {
    os.environ.get("pm1", "sensor.airmonitor01_pm_1_m_weight_concentration"): "pm1",
    os.environ.get("pm25", "sensor.airmonitor01_pm_2_5_m_weight_concentration"): "pm25",
    os.environ.get("pm10", "sensor.airmonitor01_pm_10_m_weight_concentration"): "pm10",
}

# Add optional entities if they exist
optional_entities = [
    ("TEMPERATURE_ENTITY", "temperature"),
    ("HUMIDITY_ENTITY", "humidity"),
    ("AMMONIA_ENTITY", "nh3"),
    ("CARBON_MONOXIDE_ENTITY", "co"),
    ("HYDROGEN_ENTITY", "h2"),
    ("ETHANOL_ENTITY", "c2h5oh"),
    ("METHANE_ENTITY", "ch4"),
    ("NITROGEN_DIOXIDE_ENTITY", "no2"),
]

for env_var, api_key in optional_entities:
    entity_id = os.environ.get(env_var)
    if entity_id:
        ENTITIES_TO_FORWARD[entity_id] = api_key

# Remove any empty entity IDs
ENTITIES_TO_FORWARD = {k: v for k, v in ENTITIES_TO_FORWARD.items() if k}


def get_ha_sensor_data():
    """
    Retrieve sensor data from Home Assistant.
    """
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }

    sensor_data = {}

    try:
        for entity_id, airmonitor_key in ENTITIES_TO_FORWARD.items():
            try:
                response = requests.get(
                    f"{HA_URL}/states/{entity_id}", 
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    state = data.get("state")

                    # Skip unavailable or unknown states
                    if state in ["unavailable", "unknown", "none", ""]:
                        logger.warning(f"Entity {entity_id} has state {state}, skipping")
                        continue

                    try:
                        # Convert state to float
                        value = float(state)
                        sensor_data[airmonitor_key] = value
                        logger.info(f"Retrieved {entity_id}: {value}")
                    except ValueError:
                        logger.error(
                            f"Could not convert state '{state}' to number for {entity_id}"
                        )
                else:
                    logger.error(
                        f"Failed to get {entity_id}: {response.status_code} - {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {entity_id}: {e}")

        return sensor_data

    except Exception as e:
        logger.error(f"Error retrieving data from Home Assistant: {e}")
        return {}


def prepare_airmonitor_data(sensor_data):
    """
    Prepare data for sending to AirMonitor API.
    """
    if not sensor_data:
        return None

    # Round values to integers as required by the API
    data = {k: round(v) for k, v in sensor_data.items()}

    # Add required metadata
    data["lat"] = LAT
    data["long"] = LONG
    data["sensor"] = SENSOR_MODEL

    return data


def send_to_airmonitor(data, max_retries=3, retry_delay=10):
    """
    Send measurements to AirMonitor API with retry logic.
    """
    if not data:
        logger.error("No data to send to AirMonitor")
        return False

    logger.info(f"Sending data to AirMonitor API: {data}")

    headers = {
        "X-Api-Key": AIRMONITOR_API_KEY,
        "Content-Type": "application/json"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                AIRMONITOR_API_URL,
                headers=headers,
                data=json.dumps(data),
                timeout=30  # Add timeout
            )

            if response.status_code in [200, 201]:
                logger.info(f"Successfully sent data to AirMonitor: {response.json()}")
                return True
            elif response.status_code >= 500:
                # Server error, retry
                logger.warning(f"Server error ({response.status_code}), retrying in {retry_delay}s (attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                # Client error, don't retry
                logger.error(f"Failed to send data to AirMonitor: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            if attempt < max_retries - 1:
                logger.warning(f"Retrying in {retry_delay}s (attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
    
    logger.error(f"Failed to send data after {max_retries} attempts")
    return False



def validate_config():
    """Validate that all required configuration is present."""
    required_vars = ["HA_TOKEN", "AIRMONITOR_API_KEY", "LAT", "LONG"]
    missing = [var for var in required_vars if not os.environ.get(var)]

    if missing:
        logger.error(f"Missing required configuration: {', '.join(missing)}")
        return False
        
    if not ENTITIES_TO_FORWARD:
        logger.error("No valid entities configured for forwarding")
        return False
        
    return True


def main():
    """
    Main function to run the data forwarding loop.
    """
    logger.info("Starting AirMonitor data forwarder")

    if not validate_config():
        logger.error("Invalid configuration. Exiting.")
        return

    try:
        while True:
            # Get sensor data from Home Assistant
            sensor_data = get_ha_sensor_data()

            if sensor_data:
                # Prepare data for AirMonitor
                airmonitor_data = prepare_airmonitor_data(sensor_data)

                # Send data to AirMonitor
                if airmonitor_data:
                    send_to_airmonitor(airmonitor_data)
            else:
                logger.warning("No sensor data retrieved from Home Assistant")

            # Sleep until next forwarding
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("Stopping AirMonitor data forwarder")
    except Exception as error:
        logger.error(f"Caught exception: {error}")
        raise


if __name__ == "__main__":
    main()
