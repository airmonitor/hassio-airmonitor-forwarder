#!/usr/bin/with-contenv bashio

# Make sure we have access to the supervisor API
bashio::log.info "Starting AirMonitor Forwarder add-on"

# Get config values
export HA_TOKEN=$(bashio::config 'ha_token')
export HA_URL=$(bashio::config 'ha_url')
export AIRMONITOR_API_KEY=$(bashio::config 'airmonitor_api_key')
export LAT=$(bashio::config 'latitude')
export LONG=$(bashio::config 'longitude')
export SENSOR_MODEL=$(bashio::config 'sensor_model')
export SLEEP_INTERVAL=$(bashio::config 'sleep_interval')

# Get entity mappings
export PM1_ENTITY=$(bashio::config 'entities.pm1')
export PM25_ENTITY=$(bashio::config 'entities.pm25')
export PM10_ENTITY=$(bashio::config 'entities.pm10')

# Optional entities
if bashio::config.exists 'entities.temperature'; then
  export TEMPERATURE_ENTITY=$(bashio::config 'entities.temperature')
fi

if bashio::config.exists 'entities.humidity'; then
  export HUMIDITY_ENTITY=$(bashio::config 'entities.humidity')
fi

if bashio::config.exists 'entities.ammonia'; then
  export AMMONIA_ENTITY=$(bashio::config 'entities.ammonia')
fi

if bashio::config.exists 'entities.carbon_monoxide'; then
  export CARBON_MONOXIDE_ENTITY=$(bashio::config 'entities.carbon_monoxide')
fi

if bashio::config.exists 'entities.hydrogen'; then
  export HYDROGEN_ENTITY=$(bashio::config 'entities.hydrogen')
fi

if bashio::config.exists 'entities.ethanol'; then
  export ETHANOL_ENTITY=$(bashio::config 'entities.ethanol')
fi

if bashio::config.exists 'entities.methane'; then
  export METHANE_ENTITY=$(bashio::config 'entities.methane')
fi

if bashio::config.exists 'entities.nitrogen_dioxide'; then
  export NITROGEN_DIOXIDE_ENTITY=$(bashio::config 'entities.nitrogen_dioxide')
fi

# Run the Python script
python /app/airmonitor_forwarder.py
