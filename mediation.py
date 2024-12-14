"""Mediation talking to NodeMCU."""

import hashlib
import json
from typing import Any, Final

from requests import Session
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth

from homeassistant.core import HomeAssistant

from .const import (
    CONF_APIPATH,
    CONF_HOST,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_PWD,
    CONF_USR,
    CannotConnect,
    InvalidAuth,
    NodeMCUDeviceException,
)
from .test_data import DummyDeviceData, DummyDeviceInfo, DummyDeviceSpec

headers: Final = {"Content-Type": "application/json", "User-Agent": "hass-nodemcu"}

# Built-in host name, which if provided as NodeMCU "host" value
# it will fake the http calls and return test_data.py definitions instead.
# Useful to play with data structures and overall HASS behavior
# without using actual NodeMCU device.
stubHost: Final = "stub"


# an http client session with retries to ensure unreliable network
cl = Session()
cl.mount("http://", HTTPAdapter(max_retries=3))


class NMConnection:
    """Represent NodeMCU device connectivity data and offers read and update methods."""

    hass: HomeAssistant

    # connectivity data
    hostname: str
    url_base: str

    # a hashed hostname to be used as hass entity_id (instead of using mac)
    entity_id: str
    # a generated value for entity's unique_id
    generated_unique_id: str

    # http request headers
    headers: dict[str, str]
    # authentication obj
    auth: HTTPBasicAuth | None


# the json payload from /data endpoint.
NMDeviceData = dict[str, Any]
"""Convenience type for references here and there"""


def newNMConnection(hass: HomeAssistant, data: dict[str, Any]) -> NMConnection:
    """Create new prepared connection out of URI."""

    base_url = f"{data[CONF_PROTOCOL]}://{data[CONF_HOST]}:{data[CONF_PORT]}{data[CONF_APIPATH]}"
    return _newNMConnection(
        hass, data[CONF_HOST], base_url, data.get(CONF_USR), data.get(CONF_PWD)
    )


def _newNMConnection(
    hass: HomeAssistant, hostname: str, baseUrl: str, usr: str, pwd: str
) -> NMConnection:
    c = NMConnection()
    c.hass = hass

    c.hostname = hostname
    c.url_base = baseUrl
    c.headers = {"Content-Type": "application/json"}
    c.auth = None if not usr else HTTPBasicAuth(usr, pwd)

    c.generated_unique_id = hashlib.md5(c.url_base.encode()).hexdigest()
    c.entity_id = hashlib.md5(c.hostname.encode()).hexdigest()

    return c


def _doGetLowLevel(conn: NMConnection, subPath: str) -> dict[str, Any]:
    """Run GET against the device."""
    u = f"{conn.url_base}{subPath}"
    try:
        resp = cl.get(url=u, headers=headers, auth=conn.auth)
        if resp.status_code == 401:
            raise InvalidAuth()
        return resp.json()
    except ConnectionError as ex:
        raise CannotConnect(ex) from ex
    except ValueError as ex:
        raise NodeMCUDeviceException("GET", u, ex) from ex


async def _doGet(conn: NMConnection, subPath: str) -> dict[str, Any]:
    """Run GET against the device."""
    return await conn.hass.async_add_executor_job(_doGetLowLevel, conn, subPath)


def _doPost(conn: NMConnection, data: dict[str, Any]) -> None:
    u = f"{conn.url_base}/data"
    try:
        resp = cl.post(url=u, headers=headers, auth=conn.auth, data=json.dumps(data))
        if resp.status_code == 401:
            raise InvalidAuth()
        if resp.status_code != 200:
            ex = ValueError(f"NodeMCU responsed with {resp.status_code}:{resp.text}")
            raise NodeMCUDeviceException("POST", u, data, ex)
    except ConnectionError as ex:
        raise CannotConnect(ex) from ex


async def read_device_data(conn: NMConnection) -> NMDeviceData:
    """Read via GET /data endpoint."""
    if conn.hostname == stubHost:
        return DummyDeviceData
    return await _doGet(conn, "/data")


async def read_device_info(conn: NMConnection) -> dict[str, str]:
    """Read GET /info endpoint."""
    if conn.hostname == stubHost:
        return DummyDeviceInfo
    return await _doGet(conn, "/info")


async def read_device_spec(conn: NMConnection) -> dict[str, Any]:
    """Read GET /spec endpoint."""
    if conn.hostname == stubHost:
        return DummyDeviceSpec
    return await _doGet(conn, "/spec")


async def update_device_data(conn: NMConnection, data: dict[str, Any]) -> None:
    """Write POST data to /data endpoint."""
    if conn.hostname == stubHost:
        # stub hostname, print here your data or simply put a breakpoint
        # print(f"[NodeMCU stub] : POST /api/ha/data : {json.dumps(data)}")
        return None
    return await conn.hass.async_add_executor_job(_doPost, conn, data)
