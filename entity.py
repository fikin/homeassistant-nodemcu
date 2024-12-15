"""The module contains the NMBaseEntity class and related functions for NodeMCU sensors."""

from typing import Any, cast

from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .mediation import update_device_data
from .utils import deep_get, deepdict, dict_to_attr


class NMBaseEntity(CoordinatorEntity[NMDeviceCoordinator], Entity):
    """Representation of a NodeMCU sensor.

    This sensor is updated in coordinated manner i.e. many sensors
    are updated together, with single request to the device.
    """

    def __init__(
        self,
        coordinator: NMDeviceCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize a NodeMCU sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        deviceName = (
            f"{coordinator.conn.hostname} {coordinator.read_device_info["name"]}"
        )
        self.entity_id = f"{DOMAIN}.{coordinator.conn.hostname}"
        self._attr_name = f"{deviceName} {description.name}"
        self._attr_unique_id = f"{coordinator.conf_entry.unique_id} {description.name}"
        # self._attr_device_info = {
        #     "name": f"{deviceName} {description.name}",
        #     "via_device": (DOMAIN, coordinator.confEntry.entry_id),
        #     "connections": coordinator.deviceEntry.connections,
        #     "identifiers": coordinator.deviceEntry.identifiers,
        # }
        self._attr_extra_state_attributes = {"hostname": coordinator.conn.hostname}
        self._attr_device_info = coordinator.device_info

    def update_entity(self) -> None:
        """Update an entity after a device async_update()."""
        # It reads from read data "key", expecting to be a table
        # It blindly sets the table key-values to Entity attributes

        # Note: it expects the table keys are named after Entity attributes
        # in the form of "_attr_<key>"
        tbl = deep_get(self.coordinator.data, self.entity_description.key, {})
        tbl = self.on_update(tbl)
        dict_to_attr(self, cast(dict[str, Any], tbl))

    def on_update(self, tbl: dict[str, Any]) -> dict[str, Any]:
        """Subclass to do something to data before setting attributes to self."""
        return tbl


def instrument_update(e: NMBaseEntity) -> None:
    """Set up device update callback for the entity and reads/loads initial values (data)."""

    e.coordinator.async_add_listener(e.update_entity)

    # set values right after creation
    e.update_entity()


async def send_state(e: NMBaseEntity, payload: dict[str, Any]) -> None:
    """Send update request to the device."""
    await update_device_data(
        e.coordinator.conn, deepdict(e.entity_description.key, payload)
    )
    await e.coordinator.async_request_refresh()
