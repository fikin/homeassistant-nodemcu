"""Constants for the nodemcu integration."""
from typing import Final

from homeassistant.exceptions import HomeAssistantError

DOMAIN = "nodemcu"

CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_APIPATH: Final = "apipath"
CONF_PROTOCOL: Final = "protocol"
CONF_PERIOD: Final = "period"
CONF_USR: Final = "username"
CONF_PWD: Final = "password"


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class NodeMCUDeviceException(HomeAssistantError):
    """Base exception for device IO errors."""
