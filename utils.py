from logging import Logger
from typing import TypeVar, Any, Dict, Final, cast
from urllib.parse import urlparse
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.debounce import Debouncer
from homeassistant.exceptions import IntegrationError
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .mediation import (
    NMDeviceData,
    NMConnection,
    NodeMCUDeviceException,
    read_device_data,
    read_device_info,
    read_device_spec,
    update_device_data,
    newNMConnection,
)

T = TypeVar("T")

DOMAIN: Final = "nodemcu"

CONF_URI: Final = "uri"
CONF_PERIOD: Final = "period"


def dict_to_obj(o: T, d: Dict[str, Any]) -> T:
    for k, v in d.items():
        setattr(o, k, v)
    return o


def dict_to_attr(o: T, d: Dict[str, Any]) -> T:
    for k, v in d.items():
        k = f"_attr_%s" % k
        try:
            if isinstance(o.__getattribute__(k), tuple):
                v = {'__tuple__': True, 'items': v}
        except AttributeError as ex:
            print(ex)
            pass
        setattr(o, k, v)
    return o


def deep_get(d: dict[str, Any], key: str, default: Any | None = None) -> Any | None:
    """ Safely get a nested value from a dict, useful to get deep values from json data"""

    # Descend while we can
    try:
        for k in key.split("."):
            d = d[k]
    # If at any step a key is missing, return default
    except KeyError:
        return default
    # If at any step the value is not a dict...
    except TypeError:
        # ... if it's a None, return default. Assume it would be a dict.
        if d is None:
            return default
        # ... if it's something else, raise
        else:
            raise
    # If the value was found, return it
    else:
        return d


class NMDeviceCoordinator(DataUpdateCoordinator[NMDeviceData]):
    """Basically a typed DataUpdateCoordinator"""

    conn: NMConnection

    # the entry of the device, used to form child entity ids
    entry: ConfigEntry

    # device info object as dict_to_obj result of /info endpoint
    device_info: Dict[str, str]
    # device specification as json result of /data endpoint
    spec: Dict[str, Any]


async def newCoordinator(hass: HomeAssistant, logger: Logger, entry: ConfigEntry, uri: str,
                         updatePeriodSec: int) -> NMDeviceCoordinator:
    """Instantiate new update coordinator for given URI aka. NodeMCU device"""

    conn = newNMConnection(hass, uri)

    async def _updateFnc() -> NMDeviceData:
        # actual update logic, pulling data from the device
        # inline function having upvalues
        try:
            return await read_device_data(conn)
        except NodeMCUDeviceException as ex:
            raise UpdateFailed(ex) from ex

    u = urlparse(uri)
    c = NMDeviceCoordinator(
        hass=hass,
        logger=logger,
        name=str(u.hostname),
        # update data every 10sec
        update_interval=timedelta(seconds=updatePeriodSec),
        update_method=_updateFnc,
        # delay 500ms before reading the state after update
        request_refresh_debouncer=Debouncer(hass, logger, cooldown=0.5, immediate=False))
    c.conn = conn
    c.entry = entry

    try:
        c.device_info = await read_device_info(conn)
        c.spec = await read_device_spec(conn)
    except NodeMCUDeviceException as ex:
        raise IntegrationError(ex) from ex

    return c


class NMBaseEntity(CoordinatorEntity[NMDeviceCoordinator], Entity):
    """Representation of a NodeMCU sensor."""

    def __init__(
        self,
        coordinator: NMDeviceCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize a NodeMCU sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        deviceName = f"%s %s" % (coordinator.conn.hostname, coordinator.device_info["name"])
        self._attr_name = f"{deviceName} {description.name}"
        self._attr_unique_id = f"{coordinator.entry.unique_id} {description.name}"
        self._attr_device_info = {
            "name": f"{deviceName} {description.name}",
            "via_device": (DOMAIN, coordinator.entry.entry_id),
        }
        self._attr_extra_state_attributes = {"hostname": coordinator.conn.hostname}


def update_entity(e: NMBaseEntity) -> None:
    """Updates an entity after a device async_update()"""
    # It reads from read data "key", expecting to be a table
    # It blindly sets the table key-values to Entity attributes

    # Note: it expects the table keys are named after Entity attributes
    # in the form of "_attr_<key>"
    tbl = deep_get(e.coordinator.data, e.entity_description.key, {})
    dict_to_attr(e, cast(Dict[str, Any], tbl))


def instrument_update(e: NMBaseEntity) -> None:
    """Setups device update callback for the entity and loads initial values"""

    # define callback on each coordinated device update to update entity's own properties
    def _updEntityFn():
        update_entity(e)

    e.coordinator.async_add_listener(_updEntityFn)

    # set values right after creation
    update_entity(e)


def deepDict(key: str, lastValue: Any) -> Dict[str, Any]:
    """Takes key (optionally path with.) in and returns deep Dict with last key=lastValue"""
    arr = key.split(".", 1)
    if len(arr) == 1:
        return {arr[0]: lastValue}
    return {arr[0]: deepDict(arr[1], lastValue)}


async def send_state(e: NMBaseEntity, payload: Dict[str, Any]) -> None:
    """Updates the state of the device"""
    await update_device_data(e.coordinator.conn, deepDict(e.entity_description.key, payload))
