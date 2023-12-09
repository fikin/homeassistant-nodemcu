"""HASS object to coordinate update of multiple sensors (NMEntity) together via single request."""

from logging import Logger
from typing import Any
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry, DeviceInfo
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import IntegrationError

from .const import (
    CONF_HOST,
    CONF_PERIOD,
)
from .mediation import (
    NMDeviceData,
    NMConnection,
    NodeMCUDeviceException,
    read_device_data,
    read_device_info,
    read_device_spec,
    newNMConnection,
)


class NMDeviceCoordinator(DataUpdateCoordinator[NMDeviceData]):
    """
    Basically a typed DataUpdateCoordinator

    It is used to coordinate updates across many sensors (NMEntity)
    via single request.
    """

    conn: NMConnection

    # the entry of the device, used to form child entity ids
    confEntry: ConfigEntry
    deviceEntry: DeviceEntry
    deviceInfo: DeviceInfo

    # "device info" object as dict_to_obj result of upload of "/info" endpoint
    read_device_info: dict[str, str]
    # "device specification" as json result of upload of "/spec" endpoint
    read_device_spec: dict[str, Any]


async def newCoordinator(
    hass: HomeAssistant,
    logger: Logger,
    entry: ConfigEntry,
) -> NMDeviceCoordinator:
    """
    Instantiate new update coordinator for given URI aka. NodeMCU device.

    One coordinator instance for single NodeMCU device.

    It creates connection object (NMConnection) and reads device's info and spec.
    """

    conn = newNMConnection(hass, entry.data)

    try:
        device_info = await read_device_info(conn)
        spec = await read_device_spec(conn)
    except NodeMCUDeviceException as ex:
        raise IntegrationError(ex) from ex

    async def _updateFnc() -> NMDeviceData:
        # actual update logic, pulling data from the device
        # inline function having "conn" upvalue
        try:
            d = await read_device_data(conn)
            return d
        except NodeMCUDeviceException as ex:
            raise UpdateFailed(ex) from ex

    # constructor args for base class
    c = NMDeviceCoordinator(
        hass=hass,
        logger=logger,
        name=entry.data[CONF_HOST],
        # update data every 10sec
        update_interval=timedelta(seconds=entry.data[CONF_PERIOD]),
        update_method=_updateFnc,
        # delay 500ms before reading the state after update
        request_refresh_debouncer=Debouncer(
            hass, logger, cooldown=0.5, immediate=False
        ),
    )
    # own class arguments
    c.conn = conn
    c.confEntry = entry
    c.read_device_info = device_info
    c.read_device_spec = spec

    # c.deviceInfo is set by async_setup_entry
    # c.deviceEntry is set by async_setup_entry

    return c
