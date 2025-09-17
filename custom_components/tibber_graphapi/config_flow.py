"""Config flow for Tibber GraphAPI integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import TibberGraphAPI
from .const import DOMAIN, CONF_VEHICLE_INDEX, DEFAULT_SCAN_INTERVAL, DEFAULT_VEHICLE_INDEX

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_VEHICLE_INDEX, default=DEFAULT_VEHICLE_INDEX): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api = TibberGraphAPI(session, data[CONF_USERNAME], data[CONF_PASSWORD])

    try:
        # First try to authenticate
        await api.authenticate()
        _LOGGER.debug("Authentication successful")

        # Try to get schema information first
        try:
            # Test with a simple introspection query to see available fields
            schema_test = await api.execute_gql("""
                query {
                    __schema {
                        queryType {
                            fields {
                                name
                            }
                        }
                    }
                }
            """)
            _LOGGER.debug("Schema test response: %s", schema_test)
        except Exception as e:
            _LOGGER.debug("Schema introspection failed: %s", e)
        
        # Try different query structures based on reverse engineering notes
        try:
            # Try the 'me' structure as mentioned in reverse engineering
            result = await api.execute_gql("""
                query {
                    me {
                        homes {
                            id
                            vehicles {
                                id
                                batteryLevel
                                range
                                connected
                                charging
                                chargingPower
                            }
                        }
                    }
                }
            """)
            
            _LOGGER.debug("Me query response: %s", result)
            
            if not result.get("me", {}).get("homes"):
                _LOGGER.error("No homes found in Tibber account")
                raise Exception("No homes found")
                
            homes = result["me"]["homes"]
            home_id = homes[0]["id"]
            
            if not homes[0].get("vehicles"):
                _LOGGER.error("No vehicles found in Tibber account")
                raise Exception("No vehicles found")
                
            vehicles = homes[0]["vehicles"]
            
        except Exception as e:
            _LOGGER.debug("Me query failed: %s", e)
            # Fallback: try to get basic user info
            try:
                user_info = await api.execute_gql("""
                    query {
                        me {
                            id
                        }
                    }
                """)
                _LOGGER.debug("User info response: %s", user_info)
                raise Exception("Could not access vehicle data - check if vehicle is properly connected in Tibber app")
            except Exception as e2:
                _LOGGER.debug("User info query also failed: %s", e2)
                raise Exception("Authentication successful but cannot access vehicle data")
        vehicle_index = data.get(CONF_VEHICLE_INDEX, DEFAULT_VEHICLE_INDEX)
        
        if vehicle_index >= len(vehicles):
            _LOGGER.error("Vehicle index %d is out of range (max: %d)", 
                         vehicle_index, len(vehicles) - 1)
            raise Exception("Invalid vehicle index")

        vehicle = vehicles[vehicle_index]
        
        # Return info that you want to store in the config entry.
        return {
            "title": f"Vehicle {vehicle_index + 1}",
            "vehicle_id": vehicle["id"],
            "home_id": home_id
        }

    except Exception as err:
        _LOGGER.exception("Validation failed: %s", err)
        raise

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tibber GraphAPI."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except Exception as err:
                _LOGGER.exception("Failed to validate input: %s", err)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        **user_input,
                        "vehicle_id": info["vehicle_id"],
                    }
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        ) 