from typing import Any, cast
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NMDeviceCoordinator
from .mediation import update_device_data
from .utils import deep_get, dict_to_attr, deepdict


class NMBaseEntity(CoordinatorEntity[NMDeviceCoordinator], Entity):
    """
    Representation of a NodeMCU sensor.

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

        deviceName = f"%s %s" % (
            coordinator.conn.hostname,
            coordinator.read_device_info["name"],
        )
        self._attr_name = f"{deviceName} {description.name}"
        self._attr_unique_id = f"{coordinator.confEntry.unique_id} {description.name}"
        self._attr_device_info = {
            "name": f"{deviceName} {description.name}",
            "via_device": (DOMAIN, coordinator.confEntry.entry_id),
            "connections": coordinator.deviceEntry.connections,
            "identifiers": coordinator.deviceEntry.identifiers,
        }
        self._attr_extra_state_attributes = {"hostname": coordinator.conn.hostname}


def update_entity(e: NMBaseEntity) -> None:
    """
    Updates an entity after a device async_update()

    It reads data from NMDeviceCoordinator.data and updates
    NMBaseEntity directly.
    """
    # It reads from read data "key", expecting to be a table
    # It blindly sets the table key-values to Entity attributes

    # Note: it expects the table keys are named after Entity attributes
    # in the form of "_attr_<key>"
    tbl = deep_get(e.coordinator.data, e.entity_description.key, {})
    dict_to_attr(e, cast(dict[str, Any], tbl))


def instrument_update(e: NMBaseEntity) -> None:
    """Setups device update callback for the entity and reads/loads initial values (data)"""

    # define callback on each coordinated device update to update entity's own properties
    def _updEntityFn():
        update_entity(e)

    e.coordinator.async_add_listener(_updEntityFn)

    # set values right after creation
    update_entity(e)


async def send_state(e: NMBaseEntity, payload: dict[str, Any]) -> None:
    """Sends update request to the device"""
    await update_device_data(
        e.coordinator.conn, deepdict(e.entity_description.key, payload)
    )
    await e.coordinator.async_request_refresh()
