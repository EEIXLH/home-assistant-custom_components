"""Config flow to configure SmartThings."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_PLATFORM, CONF_USERNAME
from . import CONFIG_SCHEMA, DOMAIN


_LOGGER = logging.getLogger(__name__)


class IFutureHomeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        _LOGGER.error('开始配置 IFutureHomeFlowHandler')
        errors = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]


            if username in [entry.data.get(CONF_USERNAME, None) for entry in self.hass.config_entries.async_entries(DOMAIN)]:
                errors["base"] = "already_configured"
                # return self.async_abort(reason="already_configured")
            else:
                from .iFutureHomeapi import iFutureHomeApi
                huihe = iFutureHomeApi()
                try:
                    huihe.init(username, password)
                    return self.async_create_entry(title='ifututurehome_' + user_input[CONF_USERNAME], data=user_input)
                except Exception as e:
                    logging.error(e)
                    errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({"username": str, "password": str}),
            errors=errors,
        )

    async def async_step_import(self, user_input=None):
        config = CONFIG_SCHEMA(user_input)
        _LOGGER.error('开始配置 IFutureHomeFlowHandler')
        _LOGGER.error(config)

        username = config[CONF_USERNAME]
        password = config[CONF_PASSWORD]
        

        if username in [entry.data.get(CONF_USERNAME, None) for entry in self.hass.config_entries.async_entries(DOMAIN)]:
                return self.async_abort(reason="already config")
        else:
            from .iFutureHomeapi import iFutureHomeApi
            huihe = iFutureHomeApi()
            try:
                huihe.init(username, password)
                return self.async_create_entry(title='ifututurehome_' + config[CONF_USERNAME], data=config)
            except Exception as e:
                return self.async_abort(reason=str(e))

