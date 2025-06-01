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

        # Then try to get homes to verify we have access
        homes = await api.execute_gql("""
            query {
                viewer {
                    homes {
                        id
                        vehicles {
                            id
                        }
                    }
                }
            }
        """)
        
        _LOGGER.debug("Homes query response: %s", homes)
        
        if not homes.get("viewer", {}).get("homes"):
            _LOGGER.error("No homes found in Tibber account")
            raise Exception("No homes found")
            
        home = homes["viewer"]["homes"][0]
        if not home.get("vehicles"):
            _LOGGER.error("No vehicles found in Tibber home")
            raise Exception("No vehicles found")

        vehicle_index = data.get(CONF_VEHICLE_INDEX, DEFAULT_VEHICLE_INDEX)
        if vehicle_index >= len(home["vehicles"]):
            _LOGGER.error("Vehicle index %d is out of range (max: %d)", 
                         vehicle_index, len(home["vehicles"]) - 1)
            raise Exception("Invalid vehicle index")

        # Return info that you want to store in the config entry.
        return {
            "title": f"Tibber Vehicle {vehicle_index}",
            "home_id": home["id"],
            "vehicle_id": home["vehicles"][vehicle_index]["id"]
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
                        "home_id": info["home_id"],
                        "vehicle_id": info["vehicle_id"],
                    }
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        ) 