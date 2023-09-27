from typing import Final

DummyDeviceInfo: Final = {
    "manufacturer": "NodeMCU",
    "name": "Stub-NodeMCU",
    "model": "NM-Stub",
    "swVersion": "1.2.3",
    "hwVersion": "4.5.6",
}

DummyDeviceSpec: Final = {
    "sensor": [
        {
            "key": "inA0",
            "name": "Battery",
            "device_class": "battery",
            "native_unit_of_measurement": "%",
            "state_class": "measurement",
        }
    ],
    "binary_sensor": [
        {
            "key": "inD2",
            "name": "Door",
            "device_class": "door",
        }
    ],
    "switch": [
        {
            "key": "outD4",
            "name": "Dryer",
            "device_class": "switch",
        }
    ],
    "climate": [
        {
            "key": "thermostat",
            "name": "Thermostat",
        }
    ],
    "light": [
        {
            "key": "lightD6",
            "name": "Living room light",
        },
        {
            "key": "lightD7",
            "name": "Door light",
        },
        {
            "key": "lightD8",
            "name": "Entrance light",
        },
    ],
    "button": [
        {
            "key": "button1",
            "name": "Restart device",
            "device_class": "restart",
        }
    ],
}

DummyDeviceData: Final = {
    "inA0": {"native_value": 24},
    "inD2": {"is_on": True},
    "outD4": {"is_on": True},
    "thermostat": {
        "temperature_unit": "°C",
        "current_temperature": 17.35,
        "current_humidity": 57,
        "target_temperature": 21.3,
        "target_temperature_high": 22,
        "target_temperature_low": 20,
        "target_humidity": 70,
        "max_temp": 35,
        "min_temp": 7,
        "max_humidity": 99,
        "min_humidity": 30,
        #
        "hvac_mode": "heat",
        # HVACAction.COOLING = "cooling"
        # HVACAction.DRYING = "drying"
        # HVACAction.FAN = "fan"
        # HVACAction.HEATING = "heating"
        # HVACAction.IDLE = "idle"
        # HVACAction.OFF = "off"
        "hvac_action": "heating",
        # HVACMode.OFF = "off"
        # HVACMode.HEAT = "heat"
        # HVACMode.COOL = "cool"
        # HVACMode.HEAT_COOL = "heat_cool"
        # HVACMode.AUTO = "auto"
        # HVACMode.DRY = "dry"
        # HVACMode.FAN_ONLY = "fan_only"
        "hvac_modes": ["off", "heat", "cool", "heat_cool", "auto", "dry"],
        #
        "preset_mode": "eco",
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
        "preset_modes": ["none", "eco", "away", "comfort", "home", "sleep"],
        #
        "fan_mode": "on",
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
        "fan_modes": [
            "on",
            "off",
            "auto",
            "low",
            "medium",
            "high",
            "top",
            "middle",
            "focus",
            "diffuse",
        ],
        #
        "swing_mode": "on",
        # SWING_ON = "on"
        # SWING_OFF = "off"
        # SWING_BOTH = "both"
        # SWING_VERTICAL = "vertical"
        # SWING_HORIZONTAL = "horizontal"
        "swing_modes": ["on", "off", "both", "vertical", "horizontal"],
        #
        "is_aux_heat": True,
        # SUPPORT_TARGET_TEMPERATURE = 1
        # SUPPORT_TARGET_TEMPERATURE_RANGE = 2
        # SUPPORT_TARGET_HUMIDITY = 4
        # SUPPORT_FAN_MODE = 8
        # SUPPORT_PRESET_MODE = 16
        # SUPPORT_SWING_MODE = 32
        # SUPPORT_AUX_HEAT = 64
        "supported_features": 255,
    },
    "lightD6": {
        "is_on": True,
        #
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
        #
        "effect": "dim",
        "effect_list": ["dim", "blink"],
        #
        "color_temp": 267,
        "color_temp_kelvin": 3735,
        "color_mode": "color_temp",
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
        "supported_color_modes": ["color_temp", "rgbww", "hs", "xy", "white"],
        # EFFECT = 4
        # FLASH = 8
        # TRANSITION = 32
        "supported_features": 44,
    },
    "lightD7": {
        "is_on": True,
        "color_mode": "onoff",
        "supported_color_modes": ["onoff"],
    },
    "lightD8": {
        "is_on": True,
        "brightness": 50,
        "color_mode": "brightness",
        "supported_color_modes": ["brightness"],
    },
}
