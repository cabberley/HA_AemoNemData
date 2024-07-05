"""DataUpdateCoordinator for the Redback Tech integration."""

from __future__ import annotations

from datetime import datetime, timedelta

from aemonemdata import AemoNemData
from aemonemdata.exceptions import AuthError
#rom redbacktechpy.model import RedbackTechData


from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, POLLING_INTERVAL


class AemoNemUpdateCoordinator(DataUpdateCoordinator):
    """Aemo Nem Update Coordinator."""

    data: dict   #{} # [] #{} #RedbackTechData

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Aemo Nem coordinator."""
        self._au_states = entry.data["au_states"]
        try:
            self.client = AemoNemData(   async_get_clientsession(hass)
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
        #try:
            #LOGGER.debug("Fetching data from Aemo Nem: %s", self._au_states)
        minutes_now = (datetime.now()).minute
        if (minutes_now/5) - int(minutes_now/5) <0.5 or self.data is None:
            LOGGER.debug("Fetching data from Aemo Nem: %s", self._au_states)
            data = await self.client.get_aemo_data(self._au_states) #[self._au_states]) #self._au_states)
        else:
            LOGGER.debug("Not fetching data from Aemo Nem waiting for next 5min interval to start: %s", self._au_states)
            data = self.data
        #except AuthError as error:
        #    raise ConfigEntryAuthFailed(error) from error
        #else:
        #    return data
        return data