"""Config flow for nodemcu integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CannotConnect,
    InvalidAuth,
    CONF_HOST,
    CONF_PORT,
    CONF_APIPATH,
    CONF_PROTOCOL,
    CONF_USR,
    CONF_PWD,
    CONF_PERIOD,
)
from .mediation import newNMConnection

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, description={"suggested_value": "host.domain"}): str,
        vol.Required(CONF_PORT, default=80): int,
        vol.Optional(CONF_USR): str,
        vol.Optional(CONF_PWD): str,
        vol.Required(
            CONF_PERIOD, default=300, description="Polling period in sec."
        ): int,
        vol.Required(
            CONF_APIPATH, default="/api/ha", description="API endpoint path"
        ): str,
        vol.Required(CONF_PROTOCOL, default="http", description="HTTP protocol"): str,
    }
)


class NodeMCUDeviceHub:
    """Placeholder class to make tests pass."""

    async def authenticate(self, hass: HomeAssistant, data: dict[str, Any]) -> None:
        """Test if we can authenticate with the host."""
        # If you cannot connect:
        #   throw CannotConnect
        # If the authentication is wrong:
        #   throw InvalidAuth
        newNMConnection(hass, data)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USR], data[CONF_PWD]
    # )

    await NodeMCUDeviceHub().authenticate(hass, data)

    # Return info that you want to store in the config entry.
    return {"title": data[CONF_HOST]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for nodemcu."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
