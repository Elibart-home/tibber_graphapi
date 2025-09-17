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

        # For service-only integration, we just need to verify authentication
        # The actual vehicle_id and home_id will be provided when calling the service
        try:
            # Simple test to verify authentication works
            user_info = await api.execute_gql("""
                query {
                    me {
                        id
                    }
                }
            """)
            
            _LOGGER.debug("Authentication test successful: %s", user_info)
            
            # Return basic info for the config entry
            return {
                "title": "Tibber SOC Updater",
                "user_id": user_info.get("me", {}).get("id", "unknown")
            }
                
        except Exception as e:
            _LOGGER.debug("Authentication test failed: %s", e)
            raise Exception("Could not verify Tibber account access")

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