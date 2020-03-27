"""Add support for the Xiaomi TVs."""
import logging
import datetime
from .log import logger_obj
import voluptuous as vol
from homeassistant.components.media_player import ENTITY_ID_FORMAT, MediaPlayerDevice,PLATFORM_SCHEMA
from .mediaPlayerConst import (   DOMAIN)
from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv
from . import DATA_HUIHE, HuiheDevice
from . import HUIHE_DISCOVERY_NEW, DATA_HUIHE_DISPATCHERS, DATA_HUIHE_API, DOMAIN as HUIHE_DOMAIN
from homeassistant.helpers.dispatcher import async_dispatcher_connect
DEFAULT_NAME = "iFutureHome TV"
_LOGGER = logging.getLogger(__name__)


# No host is needed for configuration, however it can be set.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


# def setup_platform(hass, config, add_entities, discovery_info=None):
#     """Set up Tuya Climate devices."""
#     if discovery_info is None:
#         return
#     huihe = hass.data[DATA_HUIHE]
#     dev_ids = discovery_info.get('dev_ids')
#     devices = []
#     for dev_id in dev_ids:
#         device = huihe.get_device_by_id(dev_id)
#         if device is None:
#             continue
#         devices.append(HuiheMediaPlayer(device))
#     add_entities(devices)

async def async_setup_entry(hass, config_entry, async_add_entities):

    async def async_discover(discovery_dev_ids):
        await _async_setup_entities(hass, config_entry, async_add_entities, discovery_dev_ids)

    # 注册新设备监听
    unsub = async_dispatcher_connect(
        hass, HUIHE_DISCOVERY_NEW.format(DOMAIN), async_discover
    )
    hass.data[DATA_HUIHE][config_entry.entry_id][DATA_HUIHE_DISPATCHERS].append(unsub)

    dev_ids = hass.data[HUIHE_DOMAIN]["entities"][config_entry.entry_id]["new_devices"].get(DOMAIN, [])
    await _async_setup_entities(hass, config_entry, async_add_entities, dev_ids)


async def _async_setup_entities(
        hass, config_entry, async_add_entities, dev_ids
):
    huihe = hass.data[DATA_HUIHE][config_entry.entry_id][DATA_HUIHE_API]
    devices = []
    for dev_id in dev_ids:
        device = huihe.get_device_by_id(dev_id)
        if device is None:
            continue
        devices.append(HuiheMediaPlayer(device))
    async_add_entities(devices)
    dev_ids.clear()



class HuiheMediaPlayer(HuiheDevice, MediaPlayerDevice):
    """Represent the huihe TV for Home Assistant."""

    def __init__(self, huihe):
        """Init TV device."""
        super().__init__(huihe)
        self.entity_id = ENTITY_ID_FORMAT.format(huihe.object_id())


    @property
    def name(self):
        """Return the display name of this TV."""
        return self.huihe.name()


    @property
    def state(self):
        """Return _state variable, containing the appropriate constant."""
        return self.huihe.state()


    @property
    def assumed_state(self):
        """Indicate that state is assumed."""
        return None


    def turn_off(self):
        """
        Instruct the TV to turn sleep.

        This is done instead of turning off,
        because the TV won't accept any input when turned off. Thus, the user
        would be unable to turn the TV back on, unless it's done manually.
        """
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging turn_off tv time is"+str(nowTime))

        return self.huihe.power()


    def turn_on(self):
        """Wake the TV back up from sleep."""

        nowTime = datetime.datetime.now()
        logger_obj.warning("beging turn_on tv time is"+str(nowTime))

        return self.huihe.power()


    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return "MEDIA_TYPE_CHANNEL"
        # return None


    @property
    def media_channel(self):
        """Channel currently playing."""
        return True


    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return self.huihe.supported_features()


    def media_previous_track(self):
        """Send previous track command."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging media_previous_track tv time is"+str(nowTime))
        return self.huihe.media_previous_track()


    def media_next_track(self):
        """Send next track command."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging media_next_track tv time is ：  %s"+str(nowTime))
        return self.huihe.media_next_track()


    def select_channel_by_number(self,command):
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging select_channel_by_number tv time is：  %s"+str(nowTime))
        return self.huihe.select_channel_by_number(command)


    def select_channel_by_name(self,command):
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging select_channel_by_name tv time is：  %s"+str(nowTime))
        return self.huihe.select_channel_by_name(command)


    def volume_up(self):
        """Increase volume by one."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging volume_up tv time is：  %s"+str(nowTime))
        return self.huihe.volume_up()


    def volume_down(self):
        """Decrease volume by one."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging volume_down tv time is：  %s"+str(nowTime))
        return self.huihe.volume_down()


    def mute_volume(self, mute):
        """Mute the volume."""

        nowTime = datetime.datetime.now()
        logger_obj.warning("beging mute_volume tv time is"+str(nowTime))
        return  self.huihe.mute_volume(mute)


    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""


    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return None