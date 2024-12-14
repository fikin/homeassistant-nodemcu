from typing import Any

from homeassistant.components.light import (
    LightEntity,
    LightEntityDescription,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .entity import NMBaseEntity, instrument_update, send_state


class NMEntityLight(NMBaseEntity, LightEntity):
    """Representation of a NodeMCU sensor."""

    async def _setOnOff(self, flg: bool, params: dict[str, Any]):
        o = {"is_on": flg, **params}
        await send_state(self, o)

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: D102
        await self._setOnOff(False, kwargs)

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: D102
        await self._setOnOff(True, kwargs)

    def on_update(self, tbl: dict[str, Any]) -> dict[str, Any]:  # noqa: D102
        return {**tbl, "supported_features": _features_enum(tbl["supported_features"])}


def _features_enum(integer_value: int) -> LightEntityFeature:
    flags = [flag for flag in LightEntityFeature if integer_value & flag.value]
    return flags | LightEntityFeature(0)  # Combine flags into a single IntFlag object


def _newEntity(coordinator: NMDeviceCoordinator, spec: dict[str, Any]) -> NMEntityLight:
    desc = LightEntityDescription(**spec)
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
