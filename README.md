# AirMonitor Forwarder Add-on for Home Assistant

Add-on documentation: <https://github.com/airmonitor/hassio-airmonitor-forwarder>

This add-on forwards air quality sensor data from your Home Assistant instance to
the [AirMonitor.pl](https://airmonitor.pl) platform, allowing you to contribute to a broader air quality monitoring
network.

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FYOUR_USERNAME%2Fairmonitor-forwarder)

## Features

- Forwards particulate matter readings (PM1, PM2.5, PM10) from Home Assistant to AirMonitor.pl
- Forwards gas sensor readings (CO, NO2, NH3, H2, CH4, C2H5OH) to AirMonitor.pl
- Supports sending particle and gas measurements in separate API calls
- Configurable update interval
- Supports custom entity mapping for different sensor setups
- Runs as a native Home Assistant add-on

## Supported Sensor Models

The add-on supports the following air quality sensor models:

### Particle Sensors

| Model                                                    | Description                                   |
|----------------------------------------------------------|-----------------------------------------------|
| [SEN55](https://botland.com.pl/szukaj?s=SEN55)           | Sensirion SEN55 Environmental Sensor          |
| [SPS30](https://allegro.pl/listing?string=sps30)         | Sensirion SPS30 Particulate Matter Sensor     |
| [PMS5003](https://allegro.pl/listing?string=pms5003)     | Plantower PMS5003 Particulate Matter Sensor   |
| [PMS7003](https://allegro.pl/listing?string=pms7003)     | Plantower PMS7003 Particulate Matter Sensor   |
| [SDS011](https://allegro.pl/listing?string=sds011)       | Nova Fitness SDS011 Dust Sensor               |
| [HPMA115S0](https://allegro.pl/listing?string=hpma115s0) | Honeywell HPMA115S0 Particulate Matter Sensor |
| [SDS021](https://allegro.pl/listing?string=sds021)       | Nova Fitness SDS021 Dust Sensor               |
| [SDSESP](https://allegro.pl/listing?string=sdsesp)       | ESP-based SDS Sensor                          |
| [PTQS1005](https://allegro.pl/listing?string=ptqs1005)   | PTQS1005 Particulate Matter Sensor            |

### Gas Sensors

| Model                                                | Description                                |
|------------------------------------------------------|--------------------------------------------|
| [MICS-4514](https://allegro.pl/listing?string=mics-4514) | MICS-4514 CO, NO2, and other gas sensor   |
| [MH-Z19](https://allegro.pl/listing?string=mh-z19)       | MH-Z19 CO2 Sensor                         |
| [CCS811](https://allegro.pl/listing?string=ccs811)       | CCS811 VOC and eCO2 Sensor               |

Select the model that matches your hardware setup. If your specific model isn't listed, choose "CUSTOM".

## Installation

1. Click the "Add repository to Home Assistant" button above
2. Navigate to the Home Assistant Add-on Store
3. Find the "AirMonitor Forwarder" add-on in the list
4. Click "Install"

## Configuration

The add-on requires the following configuration:

```yaml
ha_token: "your_long_lived_access_token"
ha_url: "home assistant url"
airmonitor_api_key: "your_airmonitor_api_key"
latitude: 52.2297
longitude: 21.0122
particle_sensor_model: "PMS7003"
gas_sensor_model: "MICS-4514"
entities:
  # Particle measurements
  pm1: "sensor.particulate_matter_1um"
  pm25: "sensor.particulate_matter_25um"
  pm10: "sensor.particulate_matter_10um"

  # Gas measurements
  co: "sensor.carbon_monoxide"
  no2: "sensor.nitrogen_dioxide"
  nh3: "sensor.ammonia"
  h2: "sensor.hydrogen"
  ch4: "sensor.methane"
  c2h5oh: "sensor.ethanol"

  # Common measurements (included with both particle and gas data)
  temperature: "sensor.temperature"
  humidity: "sensor.humidity"
```

### Configuration Options

| Option                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ha_token`            | A long-lived access token for Home Assistant.<br/> 1. Log in to your Home Assistant instance <br/> 2. Navigate to your profile <br/> * Click on your username in the bottom left corner<br/> * Or go to: http://your-home-assistant:8123/profile<br/> 3. Create a Long-Lived Access Token<br/> * Scroll down to the "Long-Lived Access Tokens" section<br/> *  Click "Create Token"<br/> * Give it a name like "AirMonitor Forwarder"<br/> * Copy the token immediately (it won't be shown again)<br/> * Use this token in your script's configuration |
| `ha_url`              | Home Assistant API endpoint, example http://192.168.1.36:8123/api                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `airmonitor_api_key`  | Your API key for AirMonitor.pl                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `latitude`            | The latitude of your sensor location                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `longitude`           | The longitude of your sensor location                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `particle_sensor_model` | The model of your particle sensor (e.g., PMS7003, SDS011)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `gas_sensor_model`    | The model of your gas sensor (e.g., MICS-4514, MH-Z19)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `entities`            | Mapping of AirMonitor parameters to Home Assistant entity IDs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

### Supported Entity Types

#### Particle Measurements
- `pm1`: Particulate matter < 1.0 μm
- `pm25`: Particulate matter < 2.5 μm
- `pm10`: Particulate matter < 10 μm

#### Gas Measurements
- `co`: Carbon monoxide
- `no2`: Nitrogen dioxide
- `nh3`: Ammonia
- `h2`: Hydrogen
- `ch4`: Methane
- `c2h5oh`: Ethanol

#### Common Measurements
- `temperature`: Temperature in °C
- `humidity`: Relative humidity in %

## Prerequisites

- Home Assistant with Supervisor (Home Assistant OS, supervised installation)
- Air quality sensors already set up in Home Assistant
- An API key from AirMonitor.pl

## Getting an AirMonitor API Key

To obtain an API key for AirMonitor.pl:

1. Register at [AirMonitor.pl](https://airmonitor.pl)
2. Navigate to your profile settings
3. Request an API key for data submission

## Supported Architectures

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

## Troubleshooting

### Common Issues

- **No data being sent**: Verify your entity IDs are correct and the sensors are providing valid readings
- **Authentication errors**: Check that your Home Assistant token and AirMonitor API key are correct
- **Connection errors**: Ensure your Home Assistant instance has internet access
- **Missing gas readings**: Make sure you've configured both a gas sensor model and the corresponding entity IDs

### Logs

To view the add-on logs:

1. Navigate to the add-on page in Home Assistant
2. Click on the "Logs" tab
3. Check for any error messages or warnings

## Contributing

Contributions to improve the add-on are welcome! Please feel free to submit pull requests or open issues on
the [GitHub repository](https://github.com/YOUR_USERNAME/airmonitor-forwarder).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This add-on was inspired by the need to contribute local air quality data to broader monitoring networks
- Thanks to the Home Assistant community for their continuous support and contributions

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg

[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg

[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg

[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg

[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
