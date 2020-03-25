"""Config flow to configure SmartThings."""
import logging

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_PLATFORM, CONF_USERNAME
from . import CONFIG_SCHEMA, DOMAIN

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register('tuya')
class TuyaFlowHandler(config_entries.ConfigFlow):

    def __init__(self):
        """Create a new instance of the flow handler."""
        pass
    async def async_step_user(self, user_input=None):
        pass
    async def async_step_import(self, user_input=None):
        config = CONFIG_SCHEMA(user_input)
        _LOGGER.error('开始配置')
        _LOGGER.error(config)

        username = config[CONF_USERNAME]
        password = config[CONF_PASSWORD]
        platform = config[CONF_PLATFORM]
        
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if username == entry.data.get(CONF_USERNAME, None):
                return self.async_abort(reason="already config")

        from tuyaha import TuyaApi
        tuya = TuyaApi()
        try:
            tuya.init(username, password, platform)
            return self.async_create_entry(title='tuya_' + config[CONF_USERNAME], data=config)
        except Exception as e:
            return self.async_abort(reason=str(e))

        
        # if 'tuya' not in [entry.domain for entry in self.hass.config_entries.async_entries()]:
        #     return self.async_create_entry(title='tuya', data=user_input)
        # else:
        #     return self.async_abort(reason="already config")
