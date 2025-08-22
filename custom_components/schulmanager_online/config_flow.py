"""Config flow for Schulmanager Online integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SchulmanagerOnlineAPI, SchulmanagerOnlineAPIError, SchulmanagerOnlineAuthError
from .const import CONF_ENABLE_SCRAPING, CONF_TOKEN, DOMAIN
from .scraper import SchulmanagerOnlineScraper, SchulmanagerOnlineScraperAuthError, SchulmanagerOnlineScraperError

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): str,
        vol.Optional(CONF_ENABLE_SCRAPING, default=False): bool,
    }
)

STEP_SCRAPING_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_api_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the API input allows us to connect."""
    session = async_get_clientsession(hass)
    api = SchulmanagerOnlineAPI(data[CONF_TOKEN], session)

    try:
        if not await api.test_connection():
            raise SchulmanagerOnlineAuthError("Invalid token")
    except SchulmanagerOnlineAPIError as err:
        raise err

    return {"title": "Schulmanager Online"}


async def validate_scraping_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the scraping input allows us to connect."""
    scraper = SchulmanagerOnlineScraper(data[CONF_USERNAME], data[CONF_PASSWORD])

    try:
        if not await scraper.test_connection():
            raise SchulmanagerOnlineScraperAuthError("Invalid credentials")
    except SchulmanagerOnlineScraperError as err:
        raise err

    return {"title": "Schulmanager Online"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Schulmanager Online."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._user_input = {}

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        self._user_input.update(user_input)

        try:
            info = await validate_api_input(self.hass, user_input)
        except SchulmanagerOnlineAuthError:
            errors["base"] = "invalid_auth"
        except SchulmanagerOnlineAPIError:
            errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        if errors:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
            )

        # If scraping is enabled, proceed to scraping configuration
        if user_input.get(CONF_ENABLE_SCRAPING, False):
            return await self.async_step_scraping()

        # Create entry with API-only configuration
        return self.async_create_entry(title=info["title"], data=self._user_input)

    async def async_step_scraping(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the scraping configuration step."""
        if user_input is None:
            return self.async_show_form(
                step_id="scraping", data_schema=STEP_SCRAPING_DATA_SCHEMA
            )

        errors = {}
        self._user_input.update(user_input)

        try:
            info = await validate_scraping_input(self.hass, user_input)
        except SchulmanagerOnlineScraperAuthError:
            errors["base"] = "invalid_auth"
        except SchulmanagerOnlineScraperError:
            errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        if errors:
            return self.async_show_form(
                step_id="scraping", data_schema=STEP_SCRAPING_DATA_SCHEMA, errors=errors
            )

        # Create entry with both API and scraping configuration
        return self.async_create_entry(title=info["title"], data=self._user_input)

