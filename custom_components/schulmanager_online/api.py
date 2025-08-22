"""API client for Schulmanager Online."""
import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp
import async_timeout

from .const import API_BASE_URL, BUNDLE_VERSION

_LOGGER = logging.getLogger(__name__)


class SchulmanagerOnlineAPIError(Exception):
    """Exception to indicate a general API error."""


class SchulmanagerOnlineAuthError(Exception):
    """Exception to indicate an authentication error."""


class SchulmanagerOnlineAPI:
    """API client for Schulmanager Online."""

    def __init__(self, token: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._token = token
        self._session = session

    async def _make_request(self, module_name: str, endpoint_name: str) -> Dict[str, Any]:
        """Make a request to the Schulmanager Online API."""
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        data = {
            "bundleVersion": BUNDLE_VERSION,
            "requests": [
                {
                    "moduleName": module_name,
                    "endpointName": endpoint_name,
                }
            ],
        }

        try:
            async with async_timeout.timeout(10):
                async with self._session.post(
                    API_BASE_URL,
                    headers=headers,
                    data=json.dumps(data),
                ) as response:
                    if response.status == 401:
                        raise SchulmanagerOnlineAuthError("Invalid token")
                    
                    if response.status != 200:
                        raise SchulmanagerOnlineAPIError(
                            f"API request failed with status {response.status}"
                        )

                    response_data = await response.json()
                    return response_data

        except aiohttp.ClientError as err:
            raise SchulmanagerOnlineAPIError(f"Request failed: {err}") from err
        except asyncio.TimeoutError as err:
            raise SchulmanagerOnlineAPIError("Request timeout") from err

    async def get_letters(self) -> List[Dict[str, Any]]:
        """Get letters from Schulmanager Online."""
        try:
            response_data = await self._make_request("letters", "get-letters")
            
            if "results" not in response_data or not response_data["results"]:
                return []

            letters_data = response_data["results"][0].get("data", [])
            
            letters = []
            for letter in letters_data:
                processed_letter = {
                    "id": letter.get("id"),
                    "title": letter.get("title"),
                    "created_at": letter.get("createdAt"),
                    "read": bool(letter.get("studentStatuses", [{}])[0].get("readTimestamp"))
                }
                letters.append(processed_letter)
            
            return letters

        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.error("Failed to parse letters response: %s", err)
            raise SchulmanagerOnlineAPIError("Failed to parse API response") from err

    async def test_connection(self) -> bool:
        """Test the connection to Schulmanager Online."""
        try:
            await self.get_letters()
            return True
        except SchulmanagerOnlineAuthError:
            return False
        except SchulmanagerOnlineAPIError:
            return False

