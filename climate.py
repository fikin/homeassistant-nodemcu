from typing import Any

from homeassistant.components.climate import (
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ATTR_TARGET_TEMP_STEP,
    ATTR_TEMPERATURE,
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .entity import NMBaseEntity, instrument_update, send_state


class NMEntityClimate(NMBaseEntity, ClimateEntity):
    """Representation of a NodeMCU sensor."""

    async def async_set_temperature(self, **kwargs: Any) -> None:  # noqa: D102
        o: dict[str, Any] = {}
        if t := kwargs.get(ATTR_TEMPERATURE):
            o["target_temperature"] = t
        if t := kwargs.get(ATTR_TARGET_TEMP_LOW):
            o["target_temperature_low"] = t
        if t := kwargs.get(ATTR_TARGET_TEMP_HIGH):
            o["target_temperature_high"] = t
        if t := kwargs.get(ATTR_TARGET_TEMP_STEP):
            o["target_temperature_step"] = t
        await send_state(self, o)

    async def async_set_humidity(self, humidity: int) -> None:  # noqa: D102
        await send_state(self, {"target_humidity": humidity})

    async def async_set_fan_mode(self, fan_mode: str) -> None:  # noqa: D102
        await send_state(self, {"fan_mode": fan_mode})

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:  # noqa: D102
        await send_state(self, {"hvac_mode": hvac_mode})

    async def async_set_swing_mode(self, swing_mode: str) -> None:  # noqa: D102
        await send_state(self, {"swing_mode": swing_mode})

    async def async_set_preset_mode(self, preset_mode: str) -> None:  # noqa: D102
        await send_state(self, {"preset_mode": preset_mode})

    async def async_turn_aux_heat_on(self) -> None:  # noqa: D102
        await send_state(self, {"is_aux_heat": True})

    async def async_turn_aux_heat_off(self) -> None:  # noqa: D102
        await send_state(self, {"is_aux_heat": False})

    async def async_turn_on(self) -> None:  # noqa: D102
        await send_state(self, {"hvac_mode": "auto"})

    async def async_turn_off(self) -> None:  # noqa: D102
        await send_state(self, {"hvac_mode": "off"})


def _features_enum(integer_value: int) -> ClimateEntityFeature:
    flags = [flag for flag in ClimateEntityFeature if integer_value & flag.value]
    return flags | ClimateEntityFeature(0)  # Combine flags into a single IntFlag object


def _newEntity(
    coordinator: NMDeviceCoordinator, spec: dict[str, Any]
) -> NMEntityClimate:
    spec2 = {**spec, "supported_features": _features_enum(spec["supported_features"])}
    desc = ClimateEntityDescription(**spec2)
    e = NMEntityClimate(coordinator, desc)
    instrument_update(e)
    return e


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator: NMDeviceCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            _newEntity(coordinator, s)
            for s in coordinator.read_device_spec.get("climate", {})
        ]
    )
