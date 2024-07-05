"""Config Flow for RedbackTech integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
import uuid 

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
#from homeassistant.const import CONF_CLIENT_SECRET, CONF_CLIENT_ID
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from aemonemdata.exceptions import AuthError
from .const import DOMAIN, DEFAULT_NAME, POLLING_INTERVAL, STATES, REGIONS, LOGGER
#from .util import async_validate_connection


DATA_SCHEMA = vol.Schema(
    {
        vol.Required("display_name", default=DEFAULT_NAME): cv.string,
        vol.Required("state_qld", default=False): cv.boolean,
        vol.Required("state_nsw", default=False): cv.boolean,
        vol.Required("state_vic", default=False): cv.boolean,
        vol.Required("state_tas", default=False): cv.boolean,
        vol.Required("state_sa", default=False): cv.boolean,
    }
)


class AemoNemConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """AemoNem config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    entry: config_entries.ConfigEntry | None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AemoNemOptionsFlowHandler:
        """Get the options flow for this handler."""
        return AemoNemOptionsFlowHandler(config_entry)

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm changes to Regions."""

        errors: dict[str, str] = {}

        if user_input:
            state_qld = user_input["state_qld"]
            state_nsw = user_input["state_nsw"]
            state_vic = user_input["state_vic"]
            state_tas = user_input["state_tas"]
            state_sa = user_input["state_sa"]
            au_states = []
            if state_qld:
                au_states.append("QLD")
            if state_nsw:
                au_states.append("NSW")
            if state_vic:
                au_states.append("VIC")
            if state_tas:
                au_states.append("TAS")
            if state_sa:
                au_states.append("SA")
            self.hass.config_entries.async_update_entry(
                self.entry,
                data={
                    "state_qld": state_qld ,
                    "state_nsw": state_nsw ,
                    "state_vic": state_vic ,
                    "state_tas": state_tas ,
                    "state_sa": state_sa ,
                    "au_states": au_states, 
                },
                options={
                    POLLING_INTERVAL: 60,
                },
            )
            await self.hass.config_entries.async_reload(self.entry.entry_id)
            return self.async_abort(reason="updates_successful")
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}

        if user_input:
            state_qld = user_input["state_qld"]
            state_nsw = user_input["state_nsw"]
            state_vic = user_input["state_vic"]
            state_tas = user_input["state_tas"]
            state_sa = user_input["state_sa"]
            au_states = []
            if state_qld:
                au_states.append("QLD")
            if state_nsw:
                au_states.append("NSW")
            if state_vic:
                au_states.append("VIC")
            if state_tas:
                au_states.append("TAS")
            if state_sa:
                au_states.append("SA")
            
            unique_id = str(uuid.uuid4())
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            LOGGER.debug("au_states: %s", au_states)
            return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={
                        "state_qld": state_qld ,
                        "state_nsw": state_nsw ,
                        "state_vic": state_vic ,
                        "state_tas": state_tas ,
                        "state_sa": state_sa ,
                        "au_states": au_states, 
                    },
                    options={
                        POLLING_INTERVAL: 15,
                    },
                )
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration of the integration."""
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=DATA_SCHEMA,
        )


class AemoNemOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle AemoNem integration options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Required(
                POLLING_INTERVAL,
                default=self.config_entry.options.get(POLLING_INTERVAL, 60),
            ): int,
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))