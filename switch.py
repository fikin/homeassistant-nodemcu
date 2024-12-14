"""The module contains the switch entity for the NodeMCU integration."""

from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .entity import NMBaseEntity, instrument_update, send_state


class NMEntitySwitch(NMBaseEntity, SwitchEntity):
    """Representation of a NodeMCU sensor."""

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: D102
        await send_state(self, {"is_on": False})

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: D102
        await send_state(self, {"is_on": True})


def _newEntity(
    coordinator: NMDeviceCoordinator, spec: dict[str, Any]
) -> NMEntitySwitch:
    desc = SwitchEntityDescription(**spec)
    e = NMEntitySwitch(coordinator, desc)
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
            for s in coordinator.read_device_spec.get("switch", {})
        ]
    )
