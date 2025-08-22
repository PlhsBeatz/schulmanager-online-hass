"""The Schulmanager Online integration."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SchulmanagerOnlineAPI, SchulmanagerOnlineAPIError
from .const import (
    CONF_ENABLE_SCRAPING,
    CONF_TOKEN,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SCRAPING_SCAN_INTERVAL,
)
from .scraper import SchulmanagerOnlineScraper, SchulmanagerOnlineScraperError

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Schulmanager Online from a config entry."""
    session = async_get_clientsession(hass)
    api = SchulmanagerOnlineAPI(entry.data[CONF_TOKEN], session)

    # Initialize scraper if enabled
    scraper = None
    if entry.data.get(CONF_ENABLE_SCRAPING, False):
        scraper = SchulmanagerOnlineScraper(
            entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
        )

    coordinator = SchulmanagerOnlineDataUpdateCoordinator(hass, api, scraper)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class SchulmanagerOnlineDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API and scraper."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: SchulmanagerOnlineAPI,
        scraper: SchulmanagerOnlineScraper = None,
    ) -> None:
        """Initialize."""
        self.api = api
        self.scraper = scraper
        
        # Use different update intervals based on whether scraping is enabled
        update_interval = (
            SCRAPING_SCAN_INTERVAL if scraper else DEFAULT_SCAN_INTERVAL
        )
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self):
        """Update data via library."""
        data = {}
        
        try:
            # Always fetch API data (letters)
            letters = await self.api.get_letters()
            data.update({
                "letters": letters,
                "unread_count": sum(1 for letter in letters if not letter["read"]),
                "total_count": len(letters),
            })
            
            # Fetch scraping data if scraper is available
            if self.scraper:
                try:
                    scraping_data = await self.scraper.scrape_all_data()
                    data.update({
                        "homework": scraping_data.get("homework", []),
                        "exams": scraping_data.get("exams", []),
                        "timetable": scraping_data.get("timetable", []),
                        "appointments": scraping_data.get("appointments", []),
                    })
                except SchulmanagerOnlineScraperError as exception:
                    _LOGGER.warning("Scraping failed, continuing with API data only: %s", exception)
                    # Continue with API data only, don't fail completely
                    data.update({
                        "homework": [],
                        "exams": [],
                        "timetable": [],
                        "appointments": [],
                    })
            
            return data
            
        except SchulmanagerOnlineAPIError as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}") from exception

