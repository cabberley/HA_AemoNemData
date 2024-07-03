"""Sensor platform for Redback Tech integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, AEMONEM_COORDINATOR, AEMO_WWW, MANUFACTURER, LOGGER
from .coordinator import AemoNemUpdateCoordinator
#from .sensor_properties import (
#    ENTITY_DETAILS,
#)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up Redback Tech Sensor Entities."""
    #global redback_devices, redback_entity_details, redback_dataSet

    coordinator: AemoNemUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        AEMONEM_COORDINATOR
    ]
    LOGGER.debug("coordinator: %s", coordinator.data)
    current_price = coordinator.data["current_price"]
    current_30min_forecast = coordinator.data["current_30min_forecast"]
    LOGGER.debug("current_30min: %s", current_30min_forecast)
    sensors = []
    #redback_dataSet = "entities"
    #device_keys = current_30min_forecast.keys()
    for device_key in current_30min_forecast.keys():
    #    sensors = []
        for entity_key in current_30min_forecast[device_key].keys():
            LOGGER.debug("device_key: %s", device_key)
            LOGGER.debug("entity_key: %s", entity_key)
            LOGGER.debug("entity_data: %s", current_30min_forecast[device_key][entity_key])
            if entity_key != "forecast":
                sensors.extend([AemoNemSensorEntity(coordinator, device_key,entity_key,current_30min_forecast[device_key][entity_key])])
    async_add_entities(sensors)

class AemoNemSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of a Redback Tech Sensor Entity."""

    def __init__(self, coordinator, device_key,entity_key,entity_data):
        super().__init__(coordinator)
        self.entity_name = entity_key
        self.entity_value  = entity_data
        self.device_key=device_key
        self.entity_id = (
            "sensor.aemo_nem_"
            + device_key
            + "_"
            + entity_key
        )

    #@property
    #def ent_data(self) -> Inverters:
    #    """Handle coordinator data for entities."""
    #    return self.coordinator.data.entities[self.ent_key]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device registry information for this entity."""
        return {
            "identifiers": {(DOMAIN, self.device_key)},
            "name": "AEMO NEM Region: " + self.device_key,
            "manufacturer": MANUFACTURER,
            #"model": redback_devices[self.ent_id].model,
            #"sw_version": redback_devices[self.ent_id].sw_version,
            #"hw_version": redback_devices[self.ent_id].hw_version,
            #"serial_number": redback_devices[self.ent_id].serial_number,
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
        return self.entity_name

    @property
    def native_value(self) -> float:
        """Return the state of the entity."""
        return self.entity_value

    @property
    def entity_registry_visible_default(self) -> bool:
        """Return whether the entity should be visible by default."""
        return True

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return whether the entity should be enabled by default."""
        return True

    @property
    def extra_state_attributes(self):
        """Return additional pieces of information."""
        if self.entity_name == "current_30min_forecast":
            dataAttributes = self.coordinator.data["current_30min_forecast"][self.device_key]["forecast"]
            data = {}
            if dataAttributes is None:
                data["forecast"] = None
                #data["min_ongrid_soc_0to1"] = None
            else:
                data = {
                    "forecast": dataAttributes,
                }
            return data
        else:
            return None
    #@property
    #def native_unit_of_measurement(self):
    #    """Return native Unit of Measurement for this entity."""
    #    if ENTITY_DETAILS[self.ent_key[7:]]["unit"] is not None:
    #        return ENTITY_DETAILS[self.ent_key[7:]]["unit"]
    #    return

    #@property
    #def device_class(self) -> SensorDeviceClass:
    #    """Return entity device class."""
    #    if ENTITY_DETAILS[self.ent_key[7:]]["device_class"] is not None:
    #        return ENTITY_DETAILS[self.ent_key[7:]]["device_class"]
    #    return

    #@property
    #def suggested_display_precision(self) -> int:
    #    """Return the suggested precision for the value."""
    #    if ENTITY_DETAILS[self.ent_key[7:]]["display_precision"] is not None:
    #        return ENTITY_DETAILS[self.ent_key[7:]]["display_precision"]  # 3
    #    return

    #@property
    #def state_class(self) -> SensorStateClass:
    #    """Return the type of state class."""
    #    if ENTITY_DETAILS[self.ent_key[7:]]["state_class"] is not None:
    #        return ENTITY_DETAILS[self.ent_key[7:]]["state_class"]
    #    return

    #@property
    #def entity_category(self) -> EntityCategory:
    #    """Set category to diagnostic."""
    #    if ENTITY_DETAILS[self.ent_key[7:]]["category"] is not None:
    #        return EntityCategory.DIAGNOSTIC
    #    return
