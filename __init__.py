"""The Tibber GraphAPI integration."""
from __future__ import annotations

import logging
import asyncio
import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    CONF_VEHICLE_INDEX,
    DEFAULT_VEHICLE_INDEX,
    MUTATION_SET_VEHICLE_SOC,
    ATTR_VEHICLE_ID,
    ATTR_HOME_ID,
    ATTR_BATTERY_LEVEL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_VEHICLE_INDEX, default=DEFAULT_VEHICLE_INDEX): cv.positive_int,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tibber GraphAPI from a config entry."""
    session = async_get_clientsession(hass)
    
    api = TibberGraphAPI(
        session,
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )
    
    try:
        await api.authenticate()
    except Exception as err:
        _LOGGER.error("Failed to authenticate with Tibber: %s", err)
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = api

    # Register service
    async def set_vehicle_soc(call: ServiceCall) -> None:
        """Set vehicle state of charge."""
        vehicle_id = call.data[ATTR_VEHICLE_ID]
        home_id = call.data[ATTR_HOME_ID]
        battery_level = call.data[ATTR_BATTERY_LEVEL]

        try:
            await api.execute_gql(
                MUTATION_SET_VEHICLE_SOC,
                {
                    "vehicleId": vehicle_id,
                    "homeId": home_id,
                    "settings": [
                        {
                            "key": "offline.vehicle.batteryLevel",
                            "value": battery_level
                        }
                    ]
                }
            )
            _LOGGER.info(
                "Successfully set vehicle %s SoC to %s%%",
                vehicle_id,
                battery_level
            )
        except Exception as err:
            _LOGGER.error(
                "Failed to set vehicle %s SoC: %s",
                vehicle_id,
                err
            )

    hass.services.async_register(DOMAIN, "set_vehicle_soc", set_vehicle_soc)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class TibberGraphAPI:
    """Handle all communication with the Tibber GraphAPI."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._username = username
        self._password = password
        self._token = None
        self._headers = {
            "User-Agent": "TibberAPI/1.0.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._endpoint = "https://app.tibber.com/v4/gql"

    async def authenticate(self) -> None:
        """Authenticate with Tibber and get JWT token."""
        auth_mutation = """
        mutation {
            login(input: {email: "%s", password: "%s"}) {
                token
                refreshToken
                user {
                    id
                }
            }
        }
        """ % (self._username, self._password)

        _LOGGER.debug("Attempting to authenticate with Tibber")
        try:
            async with async_timeout.timeout(10):
                response = await self._session.post(
                    self._endpoint,
                    json={"query": auth_mutation},
                    headers=self._headers,
                )
                
                _LOGGER.debug("Authentication response status: %s", response.status)
                response_text = await response.text()
                _LOGGER.debug("Authentication response: %s", response_text)
                
                if response.status != 200:
                    raise Exception(f"Authentication failed: {response.status} - {response_text}")
                
                data = await response.json()
                if "errors" in data:
                    raise Exception(f"Authentication failed: {data['errors']}")
                
                if not data.get("data", {}).get("login", {}).get("token"):
                    raise Exception("No token received in authentication response")
                
                self._token = data["data"]["login"]["token"]
                self._headers["Authorization"] = f"Bearer {self._token}"
                _LOGGER.debug("Successfully authenticated with Tibber")

        except asyncio.TimeoutError as err:
            raise Exception("Authentication timed out") from err
        except Exception as err:
            _LOGGER.exception("Authentication failed")
            raise

    async def execute_gql(self, query: str, variables: dict = None) -> dict:
        """Execute a GraphQL query."""
        if not self._token:
            await self.authenticate()

        try:
            async with async_timeout.timeout(10):
                response = await self._session.post(
                    self._endpoint,
                    json={"query": query, "variables": variables or {}},
                    headers=self._headers,
                )
                
                if response.status == 401:
                    # Token expired, re-authenticate
                    await self.authenticate()
                    return await self.execute_gql(query, variables)
                
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"Query failed: {response.status} - {response_text}")
                
                data = await response.json()
                if "errors" in data:
                    raise Exception(f"Query failed: {data['errors']}")
                
                return data["data"]
        except Exception as err:
            _LOGGER.exception("Failed to execute GraphQL query")
            raise 