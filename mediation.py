"""Mediation talking to NodeMCU."""

import json
import hashlib
from urllib.parse import urlparse
import requests
from requests.auth import HTTPBasicAuth
from typing import Any, Dict, Final

from homeassistant.core import HomeAssistant

from .test_data import DummyDeviceData, DummyDeviceInfo, DummyDeviceSpec

headers: Final = {"Content-Type": "application/json", "User-Agent": "ha-nodemcu"}

stubHost: Final = "stub"


class NodeMCUDeviceException(Exception):
    """Base exception for device IO errors."""


class NMConnection:
    """Represents device URI, prepared for use in read/update methods"""

    hass: HomeAssistant

    # the input uri, including credentials and base url path
    uri: str

    # computed from uri
    hostname: str
    urlBase: str

    # a hashed hostname to be used as hass entity_id (instead of using mac)
    entity_id: str
    # a generated value for entity's unique_id
    generated_unique_id: str

    # http request headers
    headers: dict[str, str]
    # authentication obj
    auth: HTTPBasicAuth | None


def newNMConnection(hass: HomeAssistant, uri: str) -> NMConnection:
    """New prepared connection out of URI"""

    c = NMConnection()
    c.uri = uri
    c.hass = hass

    u = urlparse(uri)
    c.hostname = str(u.hostname)
    c.urlBase = f"%s://%s:%d%s" % (u.scheme, u.hostname, u.port or 80, u.path)
    c.headers = {"Content-Type": "application/json"}
    c.auth = None if not u.username else HTTPBasicAuth(u.username, u.password)

    c.generated_unique_id = hashlib.md5(c.urlBase.encode()).hexdigest()
    c.entity_id = hashlib.md5(c.hostname.encode()).hexdigest()

    return c


# the json payload from /data endpoint.
NMDeviceData = Dict[str, Any]
"""Convenience type for references here and there"""


def _doGetLowLevel(conn: NMConnection, subPath: str) -> Dict[str, Any]:
    # helper running GET against the device
    u = f"%s%s" % (conn.urlBase, subPath)
    try:
        resp = requests.get(url=u, headers=headers, auth=conn.auth)
        return resp.json()
    except ValueError as ex:
        raise NodeMCUDeviceException("GET", u, ex)


async def _doGet(conn: NMConnection, subPath: str) -> Dict[str, Any]:
    # helper running GET against the device
    return await conn.hass.async_add_executor_job(_doGetLowLevel, conn, subPath)


def _doPost(conn: NMConnection, data: Dict[str, Any]) -> None:
    u = f"%s%s" % (conn.urlBase, "/data")
    try:
        requests.post(url=u, headers=headers, auth=conn.auth, data=json.dumps(data))
    except ValueError as ex:
        raise NodeMCUDeviceException("POST", u, data, ex)


async def read_device_data(conn: NMConnection) -> NMDeviceData:
    """GET /data endpoint"""
    if conn.hostname == stubHost:
        return DummyDeviceData
    return await _doGet(conn, "/data")


async def read_device_info(conn: NMConnection) -> Dict[str, str]:
    """GET /info endpoint"""
    if conn.hostname == stubHost:
        return DummyDeviceInfo
    return await _doGet(conn, "/info")


async def read_device_spec(conn: NMConnection) -> Dict[str, Any]:
    """GET /spec endpoint"""
    if conn.hostname == stubHost:
        return DummyDeviceSpec
    return await _doGet(conn, "/spec")


async def update_device_data(conn: NMConnection, data: Dict[str, Any]) -> None:
    """POST the data to /data endpoint"""
    if conn.hostname == stubHost:
        # print here your data or simply put a breakpoint
        return
    return await conn.hass.async_add_executor_job(_doPost, conn, data)
