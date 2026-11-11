"""DataUpdateCoordinator for the Redback Tech integration."""

from __future__ import annotations

from datetime import datetime, timedelta
from time import monotonic

from aemonemdata import AemoNemData
from aemonemdata.exceptions import AuthError, ClientError
#rom redbacktechpy.model import RedbackTechData


from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, POLLING_INTERVAL


FAILED_UPDATE_RETRY_INTERVAL = timedelta(minutes=5)


class AemoNemUpdateCoordinator(DataUpdateCoordinator):
    """Aemo Nem Update Coordinator."""

    data: dict  

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Aemo Nem coordinator."""
        self._au_states = entry.data["au_states"]
        self._retry_at: float | None = None
        try:
            self.client = AemoNemData(async_get_clientsession(hass))
        except (AuthError, ClientError) as error:
            raise ConfigEntryNotReady(
                f"Unable to initialize AEMO dashboard client: {error}"
            ) from error
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.options[POLLING_INTERVAL]),
        )

    async def _async_update_data(self):
        """Fetch data from Aemo Nem."""
        if self._retry_at is not None and monotonic() < self._retry_at:
            raise UpdateFailed("Waiting to retry AEMO dashboard data after a failed update")
        time_now = datetime.now()
        minutes_now = time_now.minute
        seconds_now = time_now.second
        if ((minutes_now/5) - int(minutes_now/5) <0.3
                and (minutes_now/5) - int(minutes_now/5) >0.1
                or (minutes_now/5) - int(minutes_now/5) <0.2
                and seconds_now >10
                or self.data is None
                or not self.last_update_success
                ):
            LOGGER.debug("Fetching data from Aemo Nem: %s", self._au_states)
            try:
                data = await self.client.get_aemo_data(self._au_states)
            except (AuthError, ClientError) as error:
                self._retry_at = monotonic() + FAILED_UPDATE_RETRY_INTERVAL.total_seconds()
                raise UpdateFailed(f"Unable to update AEMO dashboard data: {error}") from error
            self._retry_at = None
        else:
            LOGGER.debug("Not fetching data from Aemo Nem waiting for next 5min interval to start: %s", self._au_states)
            data = self.data
        return data