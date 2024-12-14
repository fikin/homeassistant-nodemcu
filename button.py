from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .entity import NMBaseEntity, send_state


class NMEntityButton(NMBaseEntity, ButtonEntity):
    """Representation of a NodeMCU sensor."""

    async def async_press(self) -> None:  # noqa: D102
        await send_state(self, {"action": str(self.device_class)})


def _newEntity(
    coordinator: NMDeviceCoordinator, spec: dict[str, Any]
) -> NMEntityButton:
    desc = ButtonEntityDescription(**spec)
    return NMEntityButton(coordinator, desc)


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
            for s in coordinator.read_device_spec.get("button", {})
        ]
    )
