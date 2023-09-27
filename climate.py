from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    HVACMode,
    ATTR_TEMPERATURE,
    ATTR_TARGET_TEMP_LOW,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_STEP,
)

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .entity import NMBaseEntity, instrument_update, send_state
from .utils import dict_to_obj


class NMEntity(NMBaseEntity, ClimateEntity):  # type: ignore
    """Representation of a NodeMCU sensor."""

    async def async_set_temperature(self, **kwargs: Any) -> None:  # type: ignore
        o: dict[str, Any] = {}
        if t := kwargs.get(ATTR_TEMPERATURE):  # type: ignore
            o["target_temperature"] = t
        if t := kwargs.get(ATTR_TARGET_TEMP_LOW):  # type: ignore
            o["target_temperature_low"] = t
        if t := kwargs.get(ATTR_TARGET_TEMP_HIGH):  # type: ignore
            o["target_temperature_high"] = t
        if t := kwargs.get(ATTR_TARGET_TEMP_STEP):  # type: ignore
            o["target_temperature_step"] = t
        await send_state(self, o)

    async def async_set_humidity(self, humidity: int) -> None:
        await send_state(self, {"target_humidity": humidity})

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        await send_state(self, {"fan_mode": fan_mode})

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await send_state(self, {"hvac_mode": hvac_mode})

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        await send_state(self, {"swing_mode": swing_mode})

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await send_state(self, {"preset_mode": preset_mode})

    async def async_turn_aux_heat_on(self) -> None:
        await send_state(self, {"is_aux_heat": True})

    async def async_turn_aux_heat_off(self) -> None:
        await send_state(self, {"is_aux_heat": False})

    async def async_turn_on(self) -> None:
        await send_state(self, {"turn": True})

    async def async_turn_off(self) -> None:
        await send_state(self, {"turn": False})


def _newEntity(coordinator: NMDeviceCoordinator, spec: dict[str, Any]) -> NMEntity:
    desc = dict_to_obj(ClimateEntityDescription(key="TODO"), spec)
    e = NMEntity(coordinator, desc)
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
