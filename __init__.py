"""The nodemcu integration."""
from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceEntry

from .const import DOMAIN
from .coordinator import newCoordinator, NMDeviceCoordinator


# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a single NodeMCU device from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # 1. Create API instance
    # 2. Validate the API connection (and authentication)
    # 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)
    deviceCoordinator = await newCoordinator(hass, _LOGGER, entry)

    entry.unique_id = f"{DOMAIN} {deviceCoordinator.conn.generated_unique_id}"
    hass.data[DOMAIN][entry.entry_id] = deviceCoordinator

    deviceCoordinator.deviceEntry = doSetupDevice(hass, entry, deviceCoordinator)

    # first data load from the endpoint before continuing with entities setup
    await deviceCoordinator.async_config_entry_first_refresh()
    # setup all device entities (form /spec)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        doUnloadDevice(hass, entry)

    return unload_ok


def doSetupDevice(
    hass: HomeAssistant, entry: ConfigEntry, deviceCoordinator: NMDeviceCoordinator
) -> DeviceEntry:
    """register the config-entry as device info"""
    readFromDevInfo = deviceCoordinator.read_device_info
    return dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        configuration_url=f"http://%s" % deviceCoordinator.conn.hostname,
        connections={(dr.CONNECTION_NETWORK_MAC, deviceCoordinator.conn.hostname)},
        entry_type=DeviceEntryType.SERVICE,
        hw_version=readFromDevInfo["hwVersion"],
        identifiers={(DOMAIN, str(entry.unique_id))},
        manufacturer=readFromDevInfo["manufacturer"],
        model=readFromDevInfo["model"],
        name=f"%s %s" % (deviceCoordinator.conn.hostname, readFromDevInfo["name"]),
        sw_version=readFromDevInfo["swVersion"],
    )


def doUnloadDevice(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove devices that are no longer tracked"""
    router_id = None
    device_registry = dr.async_get(hass)
    devices = dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    for device_entry in devices:
        if device_entry.via_device_id is None:
            router_id = device_entry.id
            continue  # do not remove the router itself
        device_registry.async_update_device(
            device_entry.id, remove_config_entry_id=entry.entry_id
        )

    # Remove entities that are no longer tracked
    entity_registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    for entity_entry in entries:
        if entity_entry.device_id is not router_id:
            entity_registry.async_remove(entity_entry.entity_id)
