"""Redback Tech Component."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import DOMAIN, LOGGER, AEMONEM_COORDINATOR, PLATFORMS
from .coordinator import AemoNemUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AemoNem from a config entry."""

    coordinator = AemoNemUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        AEMONEM_COORDINATOR: coordinator
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    LOGGER.info("New Aemo Nem integration is setup (entry_id=%s)", entry.entry_id)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""

    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Aemo Nem config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""

    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove Aemo Nem config entry."""
    LOGGER.debug("Removing device from device registryA: %s", device_entry.id)
    LOGGER.debug("Removing device from device registryB: %s", (next(iter(device_entry.identifiers))[1])[:3])
    LOGGER.debug("Removing device from device registryC: %s", device_entry.identifiers)
    reconfig = {**entry.data}
    state = "state_"+((next(iter(device_entry.identifiers))[1])[:3]).lower()
    LOGGER.debug("state: %s", state)
    reconfig["state_"+((next(iter(device_entry.identifiers))[1])[:3]).lower()]=False
    reconfig[state]=False
    au_states = []
    if reconfig["state_qld"]:
        au_states.append("QLD")
    if reconfig["state_nsw"]:
        au_states.append("NSW")
    if reconfig["state_vic"]:
        au_states.append("VIC")
    if reconfig["state_tas"]:
        au_states.append("TAS")
    if reconfig["state_sa"]:
        au_states.append("SA")
    LOGGER.debug("au_states: %s", au_states)
    reconfig["au_states"] = au_states
    options = {**entry.options}
    LOGGER.debug("reconfig: %s", reconfig)
    hass.config_entries.async_update_entry(
            entry, data=reconfig, options=options, version=entry.version
    )
    LOGGER.debug("config_entry_after: %s",hass.config_entries.async_get_entry(entry.entry_id))
    return True
