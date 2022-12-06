from typing import Dict, Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)

from .utils import (
    DOMAIN,
    NMDeviceCoordinator,
    NMBaseEntity,
    dict_to_obj,
    send_state,
)


class NMEntity(NMBaseEntity, ButtonEntity):  # type: ignore
    """Representation of a NodeMCU sensor."""

    async def async_press(self) -> None:
        await send_state(self, {"action": str(self.device_class)})


def _newEntity(hass: HomeAssistant, coordinator: NMDeviceCoordinator, spec: Dict[str, Any]) -> NMEntity:
    desc = dict_to_obj(ButtonEntityDescription(key="TODO"), spec)
    return NMEntity(coordinator, desc)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator: NMDeviceCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([_newEntity(hass, coordinator, s) for s in coordinator.spec.get("button", {})])
