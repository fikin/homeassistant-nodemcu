from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .entity import NMBaseEntity, instrument_update


class NMEntityBinarySensor(NMBaseEntity, BinarySensorEntity):
    """Representation of a NodeMCU sensor."""


def _newEntity(
    coordinator: NMDeviceCoordinator, spec: dict[str, Any]
) -> NMEntityBinarySensor:
    desc = BinarySensorEntityDescription(**spec)
    e = NMEntityBinarySensor(coordinator, desc)
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
            for s in coordinator.read_device_spec.get("binary_sensor", {})
        ]
    )
