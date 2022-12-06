from typing import Dict, Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)

from .utils import (
    DOMAIN,
    NMDeviceCoordinator,
    NMBaseEntity,
    dict_to_obj,
    instrument_update,
    send_state,
)


class NMEntity(NMBaseEntity, SwitchEntity):  # type: ignore
    """Representation of a NodeMCU sensor."""

    async def async_turn_off(self, **kwargs: Any) -> None:
        await send_state(self, {"is_on": False})

    async def async_turn_on(self, **kwargs: Any) -> None:
        await send_state(self, {"is_on": True})


def _newEntity(hass: HomeAssistant, coordinator: NMDeviceCoordinator, spec: Dict[str, Any]) -> NMEntity:
    desc = dict_to_obj(SwitchEntityDescription(key="TODO"), spec)
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

    async_add_entities([_newEntity(hass, coordinator, s) for s in coordinator.spec.get("switch", {})])
