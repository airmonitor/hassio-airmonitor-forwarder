import json
import logging
import os
import sys
import time

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s]:%(name)s:%(message)s")
logger = logging.getLogger("AirMonitor-Forwarder")

# Configuration from environment variables
AIRMONITOR_API_URL = "https://airmonitor.pl/prod/measurements"

# Get environment variables with validation
try:
    HA_TOKEN = os.environ.get("HA_TOKEN")
    HA_URL = os.environ.get("HA_URL")
    AIRMONITOR_API_KEY = os.environ.get("AIRMONITOR_API_KEY")
    LAT = os.environ.get("LAT")
    LONG = os.environ.get("LONG")
    SENSOR_MODEL = os.environ.get("SENSOR_MODEL")

    # Use a default for SLEEP_INTERVAL if not provided
    try:
        SLEEP_INTERVAL = int(os.environ.get("SLEEP_INTERVAL", "60"))
    except (ValueError, TypeError):
        logger.warning("Invalid SLEEP_INTERVAL, using default of 60 seconds")
        SLEEP_INTERVAL = 60

except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    sys.exit(1)

# Define which Home Assistant entities to forward
ENTITIES_TO_FORWARD = {}

# Add PM entities if they exist
pm_entities = [
    ("PM1_ENTITY", "pm1"),
    ("PM25_ENTITY", "pm25"),
    ("PM10_ENTITY", "pm10"),
]

for env_var, api_key in pm_entities:
    entity_id = os.environ.get(env_var)
    if entity_id and entity_id.lower() != "null":
        ENTITIES_TO_FORWARD[entity_id] = api_key

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
    if entity_id and entity_id.lower() != "null":
        ENTITIES_TO_FORWARD[entity_id] = api_key

# Log the configuration
logger.info(f"HA_URL: {HA_URL}")
logger.info(f"AIRMONITOR_API_URL: {AIRMONITOR_API_URL}")
logger.info(f"LAT: {LAT}, LONG: {LONG}")
logger.info(f"SENSOR_MODEL: {SENSOR_MODEL}")
logger.info(f"SLEEP_INTERVAL: {SLEEP_INTERVAL}")
logger.info(f"Entities to forward: {ENTITIES_TO_FORWARD}")

# Remove any empty entity IDs
ENTITIES_TO_FORWARD = {k: v for k, v in ENTITIES_TO_FORWARD.items() if k}


def get_ha_sensor_data():
    """
    Parameters:
        None

    Functionality:
        Retrieves sensor data from Home Assistant API.
        - Validates that the Home Assistant token is set
        - Tests authentication with the Home Assistant API
        - Iterates through configured entities and retrieves their states
        - Converts entity states to float values
        - Skips entities with unavailable, unknown, none, or empty states
        - Handles various error conditions including authentication failures,
          API errors, and value conversion errors

    Returns:
        dict: A dictionary mapping AirMonitor keys to sensor values.
              Returns an empty dictionary if any errors occur or if no
              valid data is retrieved.
    """
    if not HA_TOKEN:
        logger.error("Home Assistant token is not set")
        return {}

    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }

    # Test the authentication first
    try:
        logger.info("Testing Home Assistant API authentication...")
        test_response = requests.get(
            f"{HA_URL}/",
            headers=headers,
            timeout=10,
        )

        if test_response.status_code == 401:
            logger.error("Authentication failed: Invalid token or insufficient permissions")
            logger.error("Please create a new long-lived access token in Home Assistant")
            return {}
        elif test_response.status_code != 200:
            logger.error(f"API test failed with status code: {test_response.status_code}")
            logger.error(f"Response: {test_response.text}")
            return {}
        else:
            logger.info("Authentication successful")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error testing API: {e}")
        return {}

    sensor_data = {}

    try:
        for entity_id, airmonitor_key in ENTITIES_TO_FORWARD.items():
            try:
                response = requests.get(
                    f"{HA_URL}/states/{entity_id}",
                    headers=headers,
                    timeout=10,
                )

                if response.status_code == 200:
                    data = response.json()
                    state = data.get("state")

                    # Skip unavailable or unknown states
                    if state in {"unavailable", "unknown", "none", ""}:
                        logger.warning(f"Entity {entity_id} has state {state}, skipping")
                        continue

                    try:
                        # Convert state to float
                        value = float(state)
                        sensor_data[airmonitor_key] = value
                        logger.info(f"Retrieved {entity_id}: {value}")
                    except ValueError:
                        logger.error(
                            f"Could not convert state '{state}' to number for {entity_id}",
                        )
                else:
                    logger.error(
                        f"Failed to get {entity_id}: {response.status_code} - {response.text}",
                    )
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {entity_id}: {e}")

        return sensor_data

    except Exception as e:
        logger.error(f"Error retrieving data from Home Assistant: {e}")
        return {}


def prepare_airmonitor_data(sensor_data):
    """
    Parameters:
        sensor_data (dict): Dictionary containing sensor measurements with keys
                           representing sensor types (e.g., 'pm10', 'temperature')
                           and values as floating-point measurements.

    Functionality:
        Prepares sensor data for submission to the AirMonitor API by:
        - Validating that sensor data exists
        - Rounding all measurement values to integers as required by the API
        - Adding required metadata (latitude, longitude, sensor model)
        - The metadata values are taken from environment variables (LAT, LONG, SENSOR_MODEL)

    Returns:
        dict: A dictionary containing the formatted data ready for submission to AirMonitor API,
              including rounded sensor values and required metadata.
              Returns None if no sensor data is provided.
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


def send_to_airmonitor(data):
    """
    Parameters:
        data (dict): Dictionary containing the formatted sensor data to be sent to AirMonitor API,
                    including measurements and required metadata (lat, long, sensor).

    Functionality:
        Sends the provided sensor data to the AirMonitor API.
        - Validates that data is not empty
        - Logs the data being sent
        - Sets up proper headers including API key
        - Makes a POST request to the AirMonitor API
        - Handles different response status codes:
          * 200/201: Success
          * 500+: Server errors (potentially retryable)
          * Other: Client errors (non-retryable)
        - Catches and logs any request exceptions

    Returns:
        bool: True if data was successfully sent to AirMonitor, False otherwise
    """
    if not data:
        logger.error("No data to send to AirMonitor")
        return False

    logger.info(f"Sending data to AirMonitor API: {data}")

    headers = {
        "X-Api-Key": AIRMONITOR_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            AIRMONITOR_API_URL,
            headers=headers,
            data=json.dumps(data),
            timeout=30,  # Add timeout
        )

        if response.status_code in {200, 201}:
            logger.info(f"Successfully sent data to AirMonitor: {response.json()}")
            return True
        elif response.status_code >= 500:
            # Server error, retry
            logger.warning(f"Server error ({response.status_code})")
        else:
            # Client error, don't retry
            logger.error(f"Failed to send data to AirMonitor: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")

    logger.error("Failed to send data to AirMonitor")
    return False


def validate_config():
    """
    Parameters:
        None

    Functionality:
        Validates the application configuration by:
        - Checking that all required environment variables are set (HA_TOKEN, HA_URL,
          AIRMONITOR_API_KEY, LAT, LONG)
        - Verifying that at least one entity is configured for forwarding
        - Logs error messages for any missing configuration

    Returns:
        bool: True if the configuration is valid, False otherwise
    """
    required_vars = {["HA_TOKEN", "HA_URL", "AIRMONITOR_API_KEY", "LAT", "LONG"]}
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
    Parameters:
        None

    Functionality:
        Main entry point for the AirMonitor data forwarder application.
        - Initializes the application with a startup log message
        - Validates the configuration using validate_config()
        - Exits if configuration is invalid
        - Enters a continuous loop that:
          * Retrieves sensor data from Home Assistant
          * Prepares the data for AirMonitor if data was retrieved
          * Sends the prepared data to AirMonitor
          * Logs a warning if no sensor data was retrieved
          * Sleeps for the configured interval before the next cycle
        - Handles KeyboardInterrupt for graceful shutdown
        - Catches and logs other exceptions, then re-raises them

    Returns:
        None
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
            time.sleep(int(SLEEP_INTERVAL))

    except KeyboardInterrupt:
        logger.info("Stopping AirMonitor data forwarder")
    except Exception as error:
        logger.error(f"Caught exception: {error}")
        raise


if __name__ == "__main__":
    main()
