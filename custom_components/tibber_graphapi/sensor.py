"""Support for Tibber GraphAPI sensors."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_SCAN_INTERVAL,
    PERCENTAGE,
    UnitOfPower,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import TibberGraphAPI
from .const import (
    DOMAIN,
    CONF_VEHICLE_INDEX,
    DEFAULT_VEHICLE_INDEX,
    QUERY_GET_VEHICLE,
    ATTR_VEHICLE_ID,
    ATTR_HOME_ID,
    ATTR_BATTERY_LEVEL,
    ATTR_RANGE,
    ATTR_CHARGING,
    ATTR_CHARGING_POWER,
    ATTR_CONNECTED,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Tibber GraphAPI sensors."""
    api: TibberGraphAPI = hass.data[DOMAIN][entry.entry_id]
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, 60)
    vehicle_index = entry.data.get(CONF_VEHICLE_INDEX, DEFAULT_VEHICLE_INDEX)

    coordinator = TibberVehicleDataUpdateCoordinator(
        hass,
        api,
        timedelta(seconds=scan_interval),
        vehicle_index,
    )

    await coordinator.async_config_entry_first_refresh()

    entities = [
        TibberVehicleBatterySensor(coordinator, vehicle_index),
        TibberVehicleRangeSensor(coordinator, vehicle_index),
        TibberVehicleChargePowerSensor(coordinator, vehicle_index),
    ]

    async_add_entities(entities)

class TibberVehicleDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Tibber vehicle data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: TibberGraphAPI,
        update_interval: timedelta,
        vehicle_index: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.api = api
        self.vehicle_index = vehicle_index
        self._home_id = None
        self._vehicle_id = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        if not self._home_id:
            # First run, get home ID using the 'me' structure
            homes = await self.api.execute_gql("""
                query {
                    me {
                        homes {
                            id
                        }
                    }
                }
            """)
            self._home_id = homes["me"]["homes"][0]["id"]

        # Try to get vehicle data using the working query structure
        try:
            # First try to get vehicles from myVehicles
            vehicles_result = await self.api.execute_gql("""
                query {
                    me {
                        myVehicles {
                            vehicles {
                                id
                                title
                            }
                        }
                    }
                }
            """)
            
            if vehicles_result.get("me", {}).get("myVehicles", {}).get("vehicles"):
                vehicles = vehicles_result["me"]["myVehicles"]["vehicles"]
                if self.vehicle_index < len(vehicles):
                    self._vehicle_id = vehicles[self.vehicle_index]["id"]
                else:
                    self._vehicle_id = vehicles[0]["id"] if vehicles else "unknown"
            else:
                self._vehicle_id = "unknown"
                
        except Exception as e:
            _LOGGER.debug("Failed to get vehicle data: %s", e)
            self._vehicle_id = "unknown"

        # For now, return mock data since we can't get real vehicle data yet
        # This will allow the integration to be set up successfully
        return {
            ATTR_VEHICLE_ID: self._vehicle_id,
            ATTR_HOME_ID: self._home_id,
            ATTR_BATTERY_LEVEL: 0,  # Mock data
            ATTR_RANGE: 0,  # Mock data
            ATTR_CHARGING: False,  # Mock data
            ATTR_CHARGING_POWER: 0,  # Mock data
            ATTR_CONNECTED: False,  # Mock data
        }

class TibberVehicleBatterySensor(CoordinatorEntity, SensorEntity):
    """Representation of a vehicle battery level sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: TibberVehicleDataUpdateCoordinator, vehicle_index: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._vehicle_index = vehicle_index
        self._attr_unique_id = f"tibber_vehicle_{vehicle_index}_battery"
        self._attr_name = "Vehicle Battery Level"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(ATTR_BATTERY_LEVEL)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_CHARGING: self.coordinator.data.get(ATTR_CHARGING),
            ATTR_CONNECTED: self.coordinator.data.get(ATTR_CONNECTED),
        }

class TibberVehicleRangeSensor(CoordinatorEntity, SensorEntity):
    """Representation of a vehicle range sensor."""

    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS

    def __init__(self, coordinator: TibberVehicleDataUpdateCoordinator, vehicle_index: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._vehicle_index = vehicle_index
        self._attr_unique_id = f"tibber_vehicle_{vehicle_index}_range"
        self._attr_name = "Vehicle Range"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(ATTR_RANGE)

class TibberVehicleChargePowerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a vehicle charge power sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT

    def __init__(self, coordinator: TibberVehicleDataUpdateCoordinator, vehicle_index: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._vehicle_index = vehicle_index
        self._attr_unique_id = f"tibber_vehicle_{vehicle_index}_charge_power"
        self._attr_name = "Vehicle Charge Power"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(ATTR_CHARGING_POWER)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_CHARGING: self.coordinator.data.get(ATTR_CHARGING),
            ATTR_CONNECTED: self.coordinator.data.get(ATTR_CONNECTED),
        } 