"""Config flow for Radio Thermostat integration."""
from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol  # type: ignore

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .utils import CONF_PERIOD, CONF_URI

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain="nodemcu"):
    """Handle a config flow for NodeMCU."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return await self.create_entry_from_uri(user_input[CONF_URI], user_input[CONF_PERIOD])

        return self.async_show_form(  # type: ignore
            step_id="user",
            data_schema=vol.Schema(# type: ignore
                {
                    vol.Required(  # type: ignore
                        CONF_URI,
                        description={
                            "suggested_value":
                            "http://username:password@host:80/api"
                        }):
                    str,
                    vol.Optional(CONF_PERIOD,default=300): int # type: ignore
                }),
            errors=errors,
        )

    @callback
    async def create_entry_from_uri(self, uri: str, updatePeriodSec: int) -> FlowResult:
        """Create a config entry from NodeMCU device."""

        self._async_abort_entries_match({CONF_URI: uri})

        hostname: str = str(urlparse(uri).hostname)
        await self.async_set_unique_id(hostname, raise_on_progress=False)
        self._abort_if_unique_id_configured(updates={CONF_URI: uri})

        return self.async_create_entry(
            title=hostname,
            data={
                CONF_URI: uri,
                CONF_PERIOD: updatePeriodSec,
            },
        )
