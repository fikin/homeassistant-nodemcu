from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.humidifier import (
    HumidifierEntity,
    HumidifierEntityDescription,
    ATTR_HUMIDITY,
    ATTR_CURRENT_HUMIDITY,
    ATTR_MAX_HUMIDITY,
    ATTR_MIN_HUMIDITY,
    ATTR_MODE,
    ATTR_AVAILABLE_MODES,

)

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .entity import NMBaseEntity, instrument_update, send_state


class NMEntityHumidifier(NMBaseEntity, HumidifierEntity):  # type: ignore
    """Representation of a NodeMCU sensor."""

    async def async_set_humidity(self, humidity: int) -> None:
        await send_state(self, {"target_humidity": humidity})

    async def async_set_mode(self, mode: str) -> None:
        await send_state(self, {"mode": mode})

    async def async_turn_on(self) -> None:
        await send_state(self, {"is_on": True})

    async def async_turn_off(self) -> None:
        await send_state(self, {"is_on": False})


def _newEntity(coordinator: NMDeviceCoordinator, spec: dict[str, Any]) -> NMEntityHumidifier:
    desc = HumidifierEntityDescription(**spec)
    e = NMEntityHumidifier(coordinator, desc)
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
            for s in coordinator.read_device_spec.get("humidifier", {})
        ]
    )
