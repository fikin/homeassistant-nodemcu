"""The module contains the sensor entity for the NodeMCU integration."""

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .entity import NMBaseEntity, instrument_update


class NMEntitySensor(NMBaseEntity, SensorEntity):
    """Representation of a NodeMCU sensor."""


def _newEntity(
    coordinator: NMDeviceCoordinator, spec: dict[str, Any]
) -> NMEntitySensor:
    desc = SensorEntityDescription(**spec)
    e = NMEntitySensor(coordinator, desc)
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
            for s in coordinator.read_device_spec.get("sensor", {})
        ]
    )
