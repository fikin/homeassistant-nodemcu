"""The nodemcu integration."""
from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceEntry, DeviceInfo

from .const import DOMAIN
from .coordinator import newCoordinator, NMConnection


PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.HUMIDIFIER,
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

    # assign entry unique id using coordinator's generation logic
    if entry.unique_id is None:
        hass.config_entries.async_update_entry(
            entry, unique_id = f"{DOMAIN} {deviceCoordinator.conn.generated_unique_id}"
        )

    # store the coordinator in hass domain
    hass.data[DOMAIN][entry.entry_id] = deviceCoordinator

    # pre-create device info object, to be used by all device entries
    deviceCoordinator.deviceInfo = doSetupDeviceInfo(entry, deviceCoordinator.conn, deviceCoordinator.read_device_info)
    print(deviceCoordinator.deviceInfo)

    # do register DeviceEntry for this connector to act as hass device for all entries
    deviceCoordinator.deviceEntry = doSetupDevice(hass, entry.entry_id, deviceCoordinator.deviceInfo)

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


def doSetupDeviceInfo(
    entry: ConfigEntry, conn: NMConnection, read_device_info: dict[str, str]
) -> DeviceInfo:
    """create DeviceInfo out of config-entry"""
    return DeviceInfo(
        configuration_url=conn.urlBase,
        connections={(dr.CONNECTION_NETWORK_MAC, conn.hostname)},
        # default_manufacturer="NodeMCU",
        # default_model="NodeMCU Device",
        # default_name="NodeMCU Device",
        # entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, str(entry.unique_id))},
        manufacturer=read_device_info.get("manufacturer"),
        model=read_device_info.get("model"),
        name=f"%s %s" % (conn.hostname, read_device_info.get("name")),
        # suggested_area,
        sw_version=read_device_info.get("swVersion"),
        hw_version=read_device_info.get("hwVersion"),
        # via_device=()
    )

def doSetupDevice(
    hass: HomeAssistant, entryId: str, dInfo: DeviceInfo
) -> DeviceEntry:
    """register the config-entry as device info"""
    return dr.async_get(hass).async_get_or_create(
        config_entry_id=entryId,
        configuration_url=dInfo.get("configuration_url"),
        connections=dInfo.get("connections"),
        # entry_type=dInfo.get("entry_type"),
        hw_version=dInfo.get("hw_version"),
        identifiers=dInfo.get("identifiers"),
        manufacturer=dInfo.get("manufacturer"),
        model=dInfo.get("model"),
        name=dInfo.get("name"),
        sw_version=dInfo.get("sw_version"),
        # default_manufacturer=dInfo.get("default_manufacturer"),
        # default_model=dInfo.get("default_model"),
        # default_name=dInfo.get("default_name"),
        # suggested_area=dInfo.get("suggested_area"),
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
