"""Sensor platform for Redback Tech integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL #, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, AEMONEM_COORDINATOR, AEMO_WWW, MANUFACTURER, LOGGER
from .coordinator import AemoNemUpdateCoordinator
from .sensor_properties import (
    ENTITY_DETAILS,
)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set Up AEMO NEM Tech Sensor Entities."""

    coordinator: AemoNemUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        AEMONEM_COORDINATOR
    ]
    current_price_window = coordinator.data["current_price_window"]
    current_30min_forecast = coordinator.data["current_30min_forecast"]
    sensors = []
    for device_key in current_30min_forecast.keys():
        for entity_key in current_30min_forecast[device_key].keys():
            if (
                entity_key != "forecast" 
                and entity_key.find("flag") == -1
                and entity_key.find("flow_") == -1
                and entity_key != "interconnector_flows"
                and entity_key != "settlement_date_str"
            ):
                sensors.extend([AemoNemSensorEntity(coordinator, device_key,entity_key,current_30min_forecast[device_key][entity_key])])
            if entity_key == "interconnector_flows":
                for interconnector in current_30min_forecast[device_key][entity_key]:
                    sensors.extend([AemoNemInterconnectorSensorEntity(coordinator, device_key,interconnector["name"],interconnector)])
        for entity_key in current_price_window[device_key].keys():
            sensors.extend([AemoNemSensorEntity(coordinator, device_key,entity_key,current_price_window[device_key][entity_key]["price_kw"])])

    async_add_entities(sensors)


class AemoNemSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of a Redback Tech Sensor Entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator, device_key,entity_key,entity_data):
        super().__init__(coordinator,)
        self.entity_name = entity_key
        self.entity_value  = entity_data
        self.device_key=device_key
        self.entity_id = (
            "sensor.aemo_nem_"
            + device_key.lower()
            + "_"
            + entity_key.lower()
        )

    @callback
    def _update_callback(self) -> None:
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False
        #return True
    
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
        return ENTITY_DETAILS[self.entity_name]["name"]

    @property
    def native_value(self) -> float:
        """Return the state of the entity."""
        #return self.entity_value
        if ENTITY_DETAILS[self.entity_name]["data_set"] == "current_price_window":
            return self.coordinator.data["current_price_window"][self.device_key][self.entity_name]["price_kw"]
        elif ENTITY_DETAILS[self.entity_name]["data_set"] == "current_30min_forecast":
            return self.coordinator.data["current_30min_forecast"][self.device_key][self.entity_name]

    @property
    def entity_registry_visible_default(self) -> bool:
        """Return whether the entity should be visible by default."""
        return ENTITY_DETAILS[self.entity_name]["visible"]

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return whether the entity should be enabled by default."""
        return ENTITY_DETAILS[self.entity_name]["enabled"]
    
    @property
    def unrecorded_attributes(self):
        """Return unrecorded attributes."""
        return frozenset({MATCH_ALL})

    @property
    def extra_state_attributes(self):
        """Return additional pieces of information."""
        if self.entity_name == "current_30min_forecast":
            dataAttributes = self.coordinator.data["current_30min_forecast"][self.device_key]["forecast"]
            data = {}
            if dataAttributes is None:
                data["forecast"] = None
            else:
                data = {
                    "forecast": dataAttributes,
                }
            return data
        else:
            return None

    @property
    def native_unit_of_measurement(self):
        """Return native Unit of Measurement for this entity."""
        if ENTITY_DETAILS[self.entity_name]["unit"] is not None:
            return ENTITY_DETAILS[self.entity_name]["unit"]
        return

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""
        if ENTITY_DETAILS[self.entity_name]["device_class"] is not None:
            return ENTITY_DETAILS[self.entity_name]["device_class"]
        return

    @property
    def suggested_display_precision(self) -> int:
        """Return the suggested precision for the value."""
        if ENTITY_DETAILS[self.entity_name]["display_precision"] is not None:
            return ENTITY_DETAILS[self.entity_name]["display_precision"]  # 3
        return

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""
        if ENTITY_DETAILS[self.entity_name]["state_class"] is not None:
            return ENTITY_DETAILS[self.entity_name]["state_class"]
        return

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""
        if ENTITY_DETAILS[self.entity_name]["category"] is not None:
            return ENTITY_DETAILS[self.entity_name]["category"]
        return


class AemoNemInterconnectorSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of a Redback Tech Sensor Entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator, device_key,entity_key,entity_data):
        super().__init__(coordinator,)
        self.entity_name = entity_key
        self.entity_value  = entity_data["value"]
        self.device_key=device_key
        self.entity_id = (
            "sensor.aemo_nem_"
            + device_key.lower()
            + "_"
            + entity_key.lower()
        )

    @callback
    def _update_callback(self) -> None:
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False
    
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
        return F"Generation IC Flow - {self.entity_name}"

    @property
    def native_value(self) -> float:
        """Return the state of the entity."""
        return self.coordinator.data["current_30min_forecast"][self.device_key][f"flow_{self.entity_name}_value"]

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
        data={
            "export_limit" : self.coordinator.data["current_30min_forecast"][self.device_key][f"flow_{self.entity_name}_export_limit"],
            "import_limit" : self.coordinator.data["current_30min_forecast"][self.device_key][f"flow_{self.entity_name}_import_limit"],
        }
        return data

    @property
    def native_unit_of_measurement(self):
        """Return native Unit of Measurement for this entity."""
        return "MW"
        #UnitOfPower.MEGA_WATT - Doesn't yet have MW as a unit

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return entity device class."""
        return None #SensorDeviceClass.POWER - Doesn't yet have MW as a unit

    @property
    def suggested_display_precision(self) -> int:
        """Return the suggested precision for the value."""
        return 0

    @property
    def state_class(self) -> SensorStateClass:
        """Return the type of state class."""
        return SensorStateClass.TOTAL

    @property
    def entity_category(self) -> EntityCategory:
        """Set category to diagnostic."""
        return
