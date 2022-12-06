import logging
from typing import Final

from homeassistant.helpers.typing import ConfigType
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .utils import DOMAIN, newCoordinator, NMDeviceCoordinator, CONF_URI, CONF_PERIOD

_LOGGER = logging.getLogger(__name__)

PLATFORMS: Final = [
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]


async def async_setup(
    hass: HomeAssistant,
    config: ConfigType,
) -> bool:
    """Set up the platform."""

    # dict for all instantiated NodeMCU devices
    hass.data[DOMAIN] = {}

    # Return boolean to indicate that initialization was successful.
    return True


def _setupDevice(hass: HomeAssistant, entry: ConfigEntry, deviceCoordinator: NMDeviceCoordinator) -> None:
    # register the config-entry as device info
    di = deviceCoordinator.device_info
    dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        connections={(dr.CONNECTION_NETWORK_MAC, deviceCoordinator.conn.hostname)},
        identifiers={(DOMAIN, str(entry.unique_id))},
        manufacturer=di["manufacturer"],
        name=f"%s %s" % (deviceCoordinator.conn.hostname, di["name"]),
        model=di["model"],
        sw_version=di["swVersion"],
        hw_version=di["hwVersion"],
        configuration_url=f"http://%s" % deviceCoordinator.conn.hostname,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a single NodeMCU device from a config entry."""

    deviceCoordinator = await newCoordinator(hass, _LOGGER, entry, entry.data[CONF_URI], entry.data[CONF_PERIOD])

    entry.unique_id = f"{DOMAIN} {deviceCoordinator.conn.generated_unique_id}"
    hass.data[DOMAIN][entry.entry_id] = deviceCoordinator

    _setupDevice(hass, entry, deviceCoordinator)

    # first data load from the endpoint before continuing with entities setup
    await deviceCoordinator.async_config_entry_first_refresh()
    # setup all device entities (form /spec)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


def _unloadDevice(hass: HomeAssistant, entry: ConfigEntry) -> None:
    # Remove devices that are no longer tracked
    router_id = None
    device_registry = dr.async_get(hass)
    devices = dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    for device_entry in devices:
        if device_entry.via_device_id is None:
            router_id = device_entry.id
            continue  # do not remove the router itself
        device_registry.async_update_device(device_entry.id, remove_config_entry_id=entry.entry_id)

    # Remove entities that are no longer tracked
    entity_registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    for entity_entry in entries:
        if entity_entry.device_id is not router_id:
            entity_registry.async_remove(entity_entry.entity_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloadF = hass.config_entries.async_unload_platforms
    unload_ok = await unloadF(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    _unloadDevice(hass, entry)
    return unload_ok
