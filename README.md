# HomeAssistant NodeMCU integration

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [HomeAssistant NodeMCU integration](#homeassistant-nodemcu-integration)
  - [Introduction](#introduction)
  - [HomeAssistant Installation](#homeassistant-installation)
  - [Device integration instructions](#device-integration-instructions)
  - [NodeMCU API explained](#nodemcu-api-explained)
    - [DeviceInfo](#deviceinfo)
    - [DeviceSpec](#devicespec)
    - [DeviceData](#devicedata)
    - [Delta DeviceData](#delta-devicedata)
  - [Troubleshooting hints](#troubleshooting-hints)
    - [Using local test_data file](#using-local-test_data-file)
    - [Using provided dummy remote server](#using-provided-dummy-remote-server)
    - [Adding support for new Entity types](#adding-support-for-new-entity-types)

<!-- /code_chunk_output -->

This repository is HomeAssistant platform for integration of NodeMCU devices.

NodeMCU devices are essentially REST endpoints, implementing the generic API explained below. **Any** REST service implementing this API would be integrated by this platform.

The integration will connect to the endpoint and create all specified HomeAssistant entities. Then it would periodically poll it for data updates.

## Introduction

NodeMCU API is essentially a generic HomeAssistant device spec, not linked to any specific product.

It is plain HTTP(S) using Json as payload. Authentication is optional, for the moment based on HTTP Basic scheme.

I've designed it for integrating [NodeMCU Devices](https://github.com/fikin/nodemcu-device) devices to HomeAssistant, but it is not limited to.

The API payloads model is oriented towards actual HomeAssistant entity specific `DeviceInfo/Spec/Data` data models, which makes modelling new entity types relatively straight forward activity.

The interaction API is oriented towards periodic data poll (GET) and POST whenever data is being changed in HASS (payload is delta data).

The actual device is defining which entities it supports. And the integration platform is simply creating actual HomeAssistant device and entities. At the moment supported entity types are:

- [binary-sensor](https://developers.home-assistant.io/docs/core/entity/binary-sensor)
- [button](https://developers.home-assistant.io/docs/core/entity/button)
- [climate](https://developers.home-assistant.io/docs/core/entity/climate)
- [light](https://developers.home-assistant.io/docs/core/entity/light)
- [sensor](https://developers.home-assistant.io/docs/core/entity/sensor)
- [switch](https://developers.home-assistant.io/docs/core/entity/switch)
- [humidifier](https://developers.home-assistant.io/docs/core/entity/humidifier)

The integration supports `mDNS` (zeroconf) detection of devices which advertise as `_nodemcu-ha._tcp.local`, having property `path` containing the path to device's HTTP endpoint serving HASS integration.

## HomeAssistant Installation

- Navigate to HomeAssistant `config/custom_components` folder
- `git clone <this repository> nodemcu`
- restart HomeAssistant

## Device integration instructions

To integration NodeMCU device:

- navigate to `Settings` menu, choose `Devices&Services`, choose `Integrations` tab, press `Add Integration`, find `NodeMCU` integration
- enter device `base URI`
  - the value is generic syntax `URI` schema
  - a valid uri would include following parts `scheme://host/basePath`
  - user can optionally provide HTTP-Basic authentication in the format `scheme://user:pswd@host/basePath`
  - user can also optionally specify port in the format `scheme://host:port/basePath`
  - `basePath` is the leading path serving NodeMCU API endpoints
- modify, if required, the data polling `period`
  - value is in seconds
  - by default it is offered 5min (300sec)
- confirm creation of the device

Upon successful integration there would be new device created, named after the `hostname`. And all the entities as defined by the device itself.

If devices advertise via `mDNS`, the device will be suggested in the `Integrations` panel. Once selected for integration, the integration sequence is same as above.

## NodeMCU API explained

The API design is consisting of `baseURI`, 4 methods and `Content-Type: application/json` for both, requests and responses:

- `GET <baseURI>/info` returning `DeviceInfo`
- `GET <baseURI>/spec` returning `DeviceSpec`
- `GET <baseURI>/data` returning `DeviceData`
- `POST <baseURI>/data` accepting `delta DeviceData`

Endpoints `/info` and `/spec` are read each time the device is loaded inside HomeAssistant.

Endpoint `GET /data` is called periodically to read device's state. This is a single call for all entities provided by this device.

Endpoint `POST /data` is called only when HomeAssistant (user or automation) sets some values to some of device entities. The calls are per individual set action.

### DeviceInfo

`DeviceInfo` is explaining some info about your device. Data is modelled after HomeAssistant [DeviceInfo](https://developers.home-assistant.io/docs/device_registry_index/#what-is-a-device) data structure, attributes named similarly.

```json
{
  "manufacturer": "<your pick, for example NodeMCU>",
  "name": "<your pick>",
  "model": "<your pick>",
  "swVersion": "<your pick>",
  "hwVersion": "<your pick>"
}
```

### DeviceSpec

`DeviceSpec` is explaining what kind of HomeAssistant entities the device exposes.

Each collection is named after HomeAssistant entity. Each item inside one collection constitute one atomic HomeAssistant entity of indicated type.

Collections are optional in the payload.

Each entry (type) content is following closely the related HomeAssistant [EntityDescription](https://github.com/home-assistant/core/blob/13a4541b7bda7808084c905e57ae938b24478c11/homeassistant/helpers/entity.py#L212) data structures: `BinarySensorEntityDescription`, `ClimateEntityDescription`, `LightEntityDescription`, `SensorEntityDescription`, `SwitchEntityDescription`.

Common to **all** items is the need to specify `key` property. Its value must point to the place inside `DeviceData` where the corresponding entity data resides. The code supports `parent.child` notation for nested attributes. For example `pinD2` and `pins.d2` would be valid values, assuming they match with `DeviceData` payload structure.

```json
{
    "sensor": [
      {
        "key": "<json path to the DeviceData property containing entity's data>",
        "name": "<entity name, appended to device name>",
        "device_class": "<one of Sensor device classes>",
        "native_unit_of_measurement": "<one of supported Sensor units>",
        "state_class": "<one of Sensor state classes>",
      }
    ],
    "binary_sensor": [
      {
        "key": "<json path to the DeviceData property containing entity's data>",
        "name": "<entity name, appended to device name>",
        "device_class": "<one of BinarySensor device classes>",
      }
    ],
    "switch": [
      {
        "key": "<json path to the DeviceData property containing entity's data>",
        "name": "<entity name, appended to device name>",
        "device_class": "<one of Switch device classes>",
      }
    ],
    "climate": [
      {
        "key": "<json path to the DeviceData property containing entity's data>",
        "name": "<entity name, appended to device name>",
      }
    ],
    "light": [
      {
        "key": "<json path to the DeviceData property containing entity's data>",
        "name": "<entity name, appended to device name>",
      }
    ],
    "button": [
      {
        "key": "<json path to the DeviceData property containing entity's data>",
        "name": "<entity name, appended to device name>",
        "device_class": "<one of Button device classes>",
      }
    ],
    "humidifier": [
        {
        "key": "<json path to the DeviceData property containing entity's data>",
        "name": "<entity name, appended to device name>",
        "device_class": "<one of Humidifier device classes>"
        }
    ],
}
```

### DeviceData

`DeviceData` is representing runtime data which is periodically polled by HomeAssistant.

It is modelled after actual HomeAssistant Entity data structure where list of properties is the same as respective python class. Properties are named same as defined in `Properties` table of respective entity (documentation). From source code pov, mapping between python class and json properties is `<PyClass>._attr_<property>`. Strictly speaking not all properties have to be provided. Read description of respective HomeAssistant entry and decide then what is needed and what not.

- [binary-sensor](https://developers.home-assistant.io/docs/core/entity/binary-sensor)
- [climate](https://developers.home-assistant.io/docs/core/entity/climate)
- [sensor](https://developers.home-assistant.io/docs/core/entity/sensor)
- [switch](https://developers.home-assistant.io/docs/core/entity/switch)

```json
{
    "<some attribute path, mentioned in DeviceSpec.sensor.key value>": {
        "native_value": 24|"<actual value of the sensor, supports float format>"
    },
    "<some attribute path, mentioned in DeviceSpec.{binary_sensor,switch}.key value>": {
        "is_on": true|false
    },
    "<some attribute path, mentioned in DeviceSpec.climate.key value>": {
        "temperature_unit": "<one of supported Climate temperature units>",
        "current_temperature": 17.35|"<actual value, float>",
        "current_humidity": 57|"<actual value if SUPPORT_TARGET_HUMIDITY, int>",
        "target_temperature": 21.3|"<target value for given preset_mode if SUPPORT_TARGET_TEMPERATURE, float>",
        "target_temperature_high": 22|"<target value for given preset_mode if SUPPORT_TARGET_TEMPERATURE_RANGE, float>",
        "target_temperature_low": 20|"<target value for given preset_mode if SUPPORT_TARGET_TEMPERATURE_RANGE, float>",
        "target_humidity": 70|"<target value if SUPPORT_TARGET_HUMIDITY, int>",
        "max_temp": 35|"<UI range limiter, not strictly needed>",
        "min_temp": 7|"<UI range limiter, not strictly needed>",
        "max_humidity": 99|"<UI range limiter, not strictly needed>",
        "min_humidity": 30|"<UI range limiter, not strictly needed>",

        "hvac_mode": "<one of HVACMode values>",
        "hvac_action": "<one of HVACAction>",
        "hvac_modes": ["<list of supported HVACMode values>"],

        "preset_mode": "<one of PRESET_MODE values, if SUPPORT_PRESET_MODE>",
        "preset_modes": ["<list of supported PRESET_MODES values>"],

        "fan_mode": "<one of FAN_MODE values, if SUPPORT_FAN_MODE>",
        "fan_modes": ["<list of supported FAN_MODES>"],

        "swing_mode": "<one of SWING_MODES value, if SUPPORT_SWING_MODE>",
        "swing_modes": ["<list of supported SWING_MODE values>"],

        "is_aux_heat": true|false|"<if SUPPORT_AUX_HEAT>",

        "supported_features": 255|"<bit-or of Climate SUPPORTED_FEATURES>",
    },
    "<some attribute path, mentioned in DeviceSpec.light.key value>": {
        "is_on": true|false,
        "color_mode": "onoff",
        "supported_color_modes": ["onoff"],
    },
    "<some attribute path, mentioned in DeviceSpec.light.key value>": {
        "is_on": true|false,
        "brightness": 50,
        "color_mode": "brightness",
        "supported_color_modes": ["brightness"],
    },
    "<some attribute path, mentioned in DeviceSpec.light.key value>": {
        "is_on": true|false,
        "brightness": 50,
        "hs_color": [128, 128],
        "max_color_temp_kelvin": 4000,
        "min_color_temp_kelvin": 2700,
        "max_mireds": 500,
        "min_mireds": 153,
        "rgb_color": [128, 128, 128],
        "rgbw_color": [128, 128, 128, 128],
        "rgbww_color": [128, 128, 128, 128, 128],
        "xy_color": [128, 128],
        "effect": "<one of effect_list values>",
        "effect_list": ["<user defined list of effects>"],
        "color_temp": 267,
        "color_temp_kelvin": 3735,
        "color_mode": "<one of COLOR_MODES>",
        "supported_color_modes": ["<list of COLOR_MODES>"],
        "supported_features": 44|"<bit-or of COLOR_SUPPORTED_FEATURES>",
    },
    "<some attribute path, mentioned in DeviceSpec.humidifier.key value>": {
        "is_on": true|false,
        "action": "<one of Humidifier actions>",
        "current_humidity": 50|"<actual value, int>",
        "target_humidity": 70|"<actual value, int>",
        "max_humidity": 100|"<actual value, int>",
        "min_humidity": 0"<actual value, int>",
        "available_modes": ["<list of supported Humidifier modes>"],
        "mode": "<one of Humidifier modes>",
        "supported_features": 1|"<bit-or of Humidifier SUPPORTED_FEATURES>"
    }
}
```

### Delta DeviceData

`Delta DeviceData` is partial content of DeviceData, containing new values for only changed values. Basically each `POST` call would be initiated by a dedicated HomeAssistant service. And payload would be identical associated key but with the new value.

Here is list of all known so far services:

```json
{
  "<some attribute path, mentioned in DeviceSpec.switch.key value>": {
    "is_on": true|false
  }
}
```

Light supports several distinct changes (services), as triggered from UI:

```json
{
  "<some attribute path, mentioned in DeviceSpec.light.key value>": {
    "is_on": true|false
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.light.key value>": {
    "is_on": true,
    "effect": "blink"
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.light.key value>": {
    "is_on": true,
    "brightness": 196
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.light.key value>": {
    "is_on": true,
    "rgbww_color": [159, 255, 207, 0, 0]
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.light.key value>": {
    "is_on": true,
    "white": 26
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.light.key value>": {
    "is_on": true,
    "color_temp": 267,
    "color_temp_kelvin": 3735
  }
}
```

Climate supports several distinct changes (services), as triggered via the UI:

```json
{
  "<some attribute path, mentioned in DeviceSpec.climate.key value>": {
    "target_temperature": 21.3|"<target value>"
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.climate.key value>": {
    "target_temperature_high": 22|"<target value>",
    "target_temperature_low": 20|"<target value>"
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.climate.key value>": {
    "target_humidity": 70|"<target value>"
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.climate.key value>": {
    "hvac_mode": "<target value>"
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.climate.key value>": {
    "preset_mode": "<target value>"
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.climate.key value>": {
    "fan_mode": "<target value>"
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.climate.key value>": {
    "swing_mode": "<target value>"
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.climate.key value>": {
    "is_aux_heat": true|false
  }
}
```

Button when pressed would generate following payload:

```json
{
  "<some attribute path, mentioned in DeviceSpec.button.key value>": {
    "action": "<device class as specified in DeviceSpec>"
  }
}
```

Humidifier supports several distinct changes (services), as triggered via the UI:

```json
{
  "<some attribute path, mentioned in DeviceSpec.humidifier.key value>": {
    "target_humidity": 21.3|"<target value>"
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.humidifier.key value>": {
    "is_on": true|false
  }
}
{
  "<some attribute path, mentioned in DeviceSpec.humidifier.key value>": {
    "mode": "<one of Humidifier modes>"
  }
}
```

Reference of various constants defined in HomeAssistance source code:

```text
Climate related:
    # HVACAction.COOLING = "cooling"
    # HVACAction.DRYING = "drying"
    # HVACAction.FAN = "fan"
    # HVACAction.HEATING = "heating"
    # HVACAction.IDLE = "idle"
    # HVACAction.OFF = "off"

    # HVACMode.OFF = "off"
    # HVACMode.HEAT = "heat"
    # HVACMode.COOL = "cool"
    # HVACMode.HEAT_COOL = "heat_cool"
    # HVACMode.AUTO = "auto"
    # HVACMode.DRY = "dry"
    # HVACMode.FAN_ONLY = "fan_only"

    # PRESET_MODES:
      # # No preset is active
      # PRESET_NONE = "none"
      # # Device is running an energy-saving mode
      # PRESET_ECO = "eco"
      # # Device is in away mode
      # PRESET_AWAY = "away"
      # # Device turn all valve full up
      # PRESET_BOOST = "boost"
      # # Device is in comfort mode
      # PRESET_COMFORT = "comfort"
      # # Device is in home mode
      # PRESET_HOME = "home"
      # # Device is prepared for sleep
      # PRESET_SLEEP = "sleep"
      # # Device is reacting to activity (e.g. movement sensors)
      # PRESET_ACTIVITY = "activity"

    # FAN_MODES:
      # FAN_ON = "on"
      # FAN_OFF = "off"
      # FAN_AUTO = "auto"
      # FAN_LOW = "low"
      # FAN_MEDIUM = "medium"
      # FAN_HIGH = "high"
      # FAN_TOP = "top"
      # FAN_MIDDLE = "middle"
      # FAN_FOCUS = "focus"
      # FAN_DIFFUSE = "diffuse"

    # SWING_MODES:
      # SWING_ON = "on"
      # SWING_OFF = "off"
      # SWING_BOTH = "both"
      # SWING_VERTICAL = "vertical"
      # SWING_HORIZONTAL = "horizontal"

    # SUPPORTED_FEATURES:
      # SUPPORT_TARGET_TEMPERATURE = 1
      # SUPPORT_TARGET_TEMPERATURE_RANGE = 2
      # SUPPORT_TARGET_HUMIDITY = 4
      # SUPPORT_FAN_MODE = 8
      # SUPPORT_PRESET_MODE = 16
      # SUPPORT_SWING_MODE = 32
      # SUPPORT_AUX_HEAT = 64

Light related:
    # COLOR_MODES:
      # UNKNOWN = "unknown"  # Ambiguous color mode
      # ONOFF = "onoff"  # Must be the only supported mode
      # BRIGHTNESS = "brightness"  # Must be the only supported mode
      # COLOR_TEMP = "color_temp"
      # HS = "hs"
      # XY = "xy"
      # RGB = "rgb"
      # RGBW = "rgbw"
      # RGBWW = "rgbww"
      # WHITE = "white"  # Must *NOT* be the only supported mode

    # COLOR_SUPPORTED_FEATURES:
      # EFFECT = 4
      # FLASH = 8
      # TRANSITION = 32

Humidifier related:
    # ACTIONS:
        # HUMIDIFYING = "humidifying"
        # DRYING = "drying"
        # IDLE = "idle"
        # OFF = "off"

    # MODES:
        # MODE_NORMAL	  = "normal" # No preset is active, normal operation
        # MODE_ECO	    = "eco" # Device is running an energy-saving mode
        # MODE_AWAY	    = "away" # Device is in away mode
        # MODE_BOOST	  = "boost" # Device turn all valve full up
        # MODE_COMFORT	= "comfort" # Device is in comfort mode
        # MODE_HOME	    = "home" # Device is in home mode
        # MODE_SLEEP	  = "sleep" # Device is prepared for sleep
        # MODE_AUTO	    = "auto" # Device is controlling humidity by itself
        # MODE_BABY	    = "baby" # Device is trying to optimize for babies
```

## Troubleshooting hints

### Using local test_data file

There is `test_data.py` which contains example integration of all presently supported entity types.

This data can be used to experiment with HomeAssistant Entity specifications and data.

The code is hardwired to recognize `stub` as special hostname (see `mediation.py`).
If you integrate a device with uri `http://stub/api` the mediation will serve the `test_data.py` data instead of talking to a remote host.

This is the simplest and fastest way to tune specifications and data.
Also when stubbed, any setting change will be printed to console like:

```text
[NodeMCU stub] : POST /api/ha/data : {"humidifier1": {"is_on": false}}
```

Note: that there is no real device behind and all entity state changes will be only momentary.

If you do really do have a legitimate hostname called `stub` and you want to integrate it, just modify `mediation.py:stubHost` variable value.

Since the hardwiring is threating the data in immutable way, issuing commands from HomeAssistant are kind of invisible. I use the dummy remote server to troubleshoot such payloads.

### Using provided dummy remote server

There is `test_web.py` which hosts `test_data.py` under `http://localhost:8080/api` endpoint.

It behaves same way as built-in internal `stub` hostname but it is responding over the net and prints all POST payloads in the terminal.

Start the server in one terminal (`python3 test_web`) and integrate device to HomeAssistant using above url.

This server can be used as boilerplate for other device implementations too.

### Adding support for new Entity types

All entity types currently are carbon copy of each other, with variations only for specific python classes used.

Feel welcome to add new types this way, just copy closest existing entity and adjust to correct classes.
