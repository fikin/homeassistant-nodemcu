from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.light import (
    LightEntity,
    LightEntityDescription,
)

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .entity import NMBaseEntity, instrument_update, send_state
from .utils import dict_to_obj


class NMEntityLight(NMBaseEntity, LightEntity):  # type: ignore
    """Representation of a NodeMCU sensor."""

    async def _setOnOff(self, flg: bool, params: dict[str, Any]):
        o = {"is_on": flg}
        for k, v in params.items():
            o[k] = v
        await send_state(self, o)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._setOnOff(False, kwargs)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._setOnOff(True, kwargs)


def _newEntity(coordinator: NMDeviceCoordinator, spec: dict[str, Any]) -> NMEntityLight:
    desc = dict_to_obj(LightEntityDescription(key="TODO"), spec)
    e = NMEntityLight(coordinator, desc)
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
            for s in coordinator.read_device_spec.get("light", {})
        ]
    )
