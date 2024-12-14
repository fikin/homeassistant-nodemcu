"""The module contains the implementation of the NodeMCU humidifier component."""

from typing import Any

from homeassistant.components.humidifier import (
    HumidifierEntity,
    HumidifierEntityDescription,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .entity import NMBaseEntity, instrument_update, send_state


class NMEntityHumidifier(NMBaseEntity, HumidifierEntity):
    """Representation of a NodeMCU sensor."""

    async def async_set_humidity(self, humidity: int) -> None:  # noqa: D102
        await send_state(self, {"target_humidity": humidity})

    async def async_set_mode(self, mode: str) -> None:  # noqa: D102
        await send_state(self, {"mode": mode})

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: D102
        await send_state(self, {"is_on": True})

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: D102
        await send_state(self, {"is_on": False})

    def on_update(self, tbl: dict[str, Any]) -> dict[str, Any]:  # noqa: D102
        return {**tbl, "supported_features": _features_enum(tbl["supported_features"])}


def _features_enum(integer_value: int) -> HumidifierEntityFeature:
    flags = [flag for flag in HumidifierEntityFeature if integer_value & flag.value]
    return flags | HumidifierEntityFeature(
        0
    )  # Combine flags into a single IntFlag object


def _newEntity(
    coordinator: NMDeviceCoordinator, spec: dict[str, Any]
) -> NMEntityHumidifier:
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
