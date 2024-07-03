"""DataUpdateCoordinator for the Redback Tech integration."""

from __future__ import annotations

from datetime import timedelta

from aemonemdata import AemoNemData
from redbacktechpy.exceptions import AuthError, RedbackTechClientError
#rom redbacktechpy.model import RedbackTechData


from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, POLLING_INTERVAL


class AemoNemUpdateCoordinator(DataUpdateCoordinator):
    """Aemo Nem Update Coordinator."""

    #data: RedbackTechData

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Aemo Nem coordinator."""
        self._au_states = entry.data["au_states"]
        try:
            self.client = AemoNemData( async_get_clientsession(hass)
            )
            super().__init__(
                hass,
                LOGGER,
                name=DOMAIN,
                update_interval=timedelta(seconds=entry.options[POLLING_INTERVAL]),
            )
        except AuthError as error:
            raise ConfigEntryAuthFailed(error) from error

    async def _async_update_data(self):
        """Fetch data from Aemo Nem."""
        try:
            LOGGER.debug("Fetching data from Aemo Nem: %s", self._au_states)
            data = await self.client.get_aemo_data(self._au_states) #[self._au_states]) #self._au_states)
            LOGGER.debug("Data from Aemo Nem: %s", data)
        except AuthError as error:
            raise ConfigEntryAuthFailed(error) from error
        except RedbackTechClientError as error:
            raise UpdateFailed(error) from error
        else:
            return data