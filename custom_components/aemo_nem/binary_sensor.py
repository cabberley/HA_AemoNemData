"""Sensor platform for Redback Tech integration."""

from __future__ import annotations
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    AEMONEM_COORDINATOR,
    AEMO_WWW,
    MANUFACTURER,
    LOGGER,
)
from .coordinator import AemoNemUpdateCoordinator
from .binary_sensor_properties import ENTITY_DETAILS


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Redback Tech Sensor Entities."""
    #global redback_devices, redback_entity_details

    coordinator: AemoNemUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        AEMONEM_COORDINATOR
    ]

    #redback_devices = coordinator.data.devices
    #redback_entity_details = coordinator.data.entities
    binary_sensors = []

    entity_keys = coordinator.data["current_30min_forecast"]["QLD1"].keys()
    device_key = "QLD1"
    # swap this around to get the binary sensors quicker
    for entity_key in entity_keys:
        if entity_key in ENTITY_DETAILS:
            binary_sensors.extend(
                [RedbackTechBinarySensorEntity(coordinator, device_key, entity_key)]
            )

    async_add_entities(binary_sensors)


class RedbackTechBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """Representation of Binary Sensor."""

    def __init__(self, coordinator, device_key, entity_key):
        super().__init__(coordinator)
        #self.ent_id = entity_key[:7]
        self.entity_key = entity_key
        self.entity_id = (
            "binary_sensor.aemonem"
            + "_"
            + device_key.lower()
            + "_"
            + entity_key #ENTITY_DETAILS[self.ent_key]["name"]
        )
        self.entity_name = entity_key
        #self.entity_value  = entity_data
        self.device_key=device_key
        
        #LOGGER.debug(f"number_data1: {self.ent_data}")
        #LOGGER.debug(f"number_data2: {self.ent_id}")

    @property
    def entity_data(self):
        """Handle coordinator data for entities."""
        return self.coordinator.data["current_30min_forecast"]["QLD1"][self.entity_name]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self.device_key)},
            "name": "AEMO NEM Region: " + self.device_key,
            "manufacturer": MANUFACTURER,
            "model": "AEMO NEM",
            #"sw_version": ,
            #"hw_version": ,
            #"serial_number": ,
            "configuration_url": AEMO_WWW,
        }

    @property
    def unique_id(self) -> str:
        """Sets unique ID for this entity."""
        return self.entity_id

    @property
    def has_entity_name(self) -> bool:
        """Indicate that entity has name defined."""
        return True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return ENTITY_DETAILS[self.entity_key]["name"]

    @property
    def icon(self) -> str:
        """Set icon for this entity, if provided in parameters."""
        if ENTITY_DETAILS[self.entity_key]["icon"] is not None:
            return ENTITY_DETAILS[self.entity_key]["icon"]
        return

    @property
    def state_color(self):
        """Return the state color."""
        return True

    @property
    def entity_registry_visible_default(self) -> bool:
        """Return whether the entity should be visible by default."""
        if ENTITY_DETAILS[self.entity_key]["visible"]:
            return True
        #elif self.ent_data.data["value"] is None:
        #    return False
        return False

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return whether the entity should be enabled by default."""
        if ENTITY_DETAILS[self.entity_key]["enabled"]:
            return True
        return False

    @property
    def is_on(self) -> bool:
        """Return the state of the entity."""
        value = self.entity_data
        if value:
            return True
        return False
