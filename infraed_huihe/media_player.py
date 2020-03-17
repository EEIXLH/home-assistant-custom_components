"""Add support for the Xiaomi TVs."""
import logging
import datetime
from .log import logger_obj
import voluptuous as vol
from homeassistant.components.media_player import ENTITY_ID_FORMAT, MediaPlayerDevice,PLATFORM_SCHEMA
from .mediaPlayerConst import (SUPPORT_VOLUME_SET,
    SUPPORT_TURN_OFF, SUPPORT_TURN_ON, SUPPORT_VOLUME_STEP,SUPPORT_PREVIOUS_TRACK,SUPPORT_NEXT_TRACK,SUPPORT_VOLUME_MUTE)
from homeassistant.const import CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON
import homeassistant.helpers.config_validation as cv
from . import DATA_INFREAD, InfraedDevice

DEFAULT_NAME = "iFutureHome TV"
_LOGGER = logging.getLogger(__name__)


# No host is needed for configuration, however it can be set.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Tuya Climate devices."""
    if discovery_info is None:
        return
    infraed = hass.data[DATA_INFREAD]
    dev_ids = discovery_info.get('dev_ids')
    devices = []
    for dev_id in dev_ids:
        device = infraed.get_device_by_id(dev_id)
        if device is None:
            continue
        devices.append(HuiheMediaPlayer(device))
    add_entities(devices)



class HuiheMediaPlayer(InfraedDevice, MediaPlayerDevice):
    """Represent the huihe TV for Home Assistant."""

    def __init__(self, infraed):
        """Init TV device."""
        super().__init__(infraed)
        self.entity_id = ENTITY_ID_FORMAT.format(infraed.object_id())


    @property
    def name(self):
        """Return the display name of this TV."""
        return self.infraed.name()


    @property
    def state(self):
        """Return _state variable, containing the appropriate constant."""
        if self.infraed.state =="on":

            return True
        else:
            return False


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

        return self.infraed.power()


    def turn_on(self):
        """Wake the TV back up from sleep."""

        nowTime = datetime.datetime.now()
        logger_obj.warning("beging turn_on tv time is"+str(nowTime))

        return self.infraed.power()


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
        return self.infraed.supported_features()


    def media_previous_track(self):
        """Send previous track command."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging media_previous_track tv time is"+str(nowTime))
        return self.infraed.media_previous_track()


    def media_next_track(self):
        """Send next track command."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging media_next_track tv time is ：  %s"+str(nowTime))
        return self.infraed.media_next_track()


    def select_channel_by_number(self,command):
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging select_channel_by_number tv time is：  %s"+str(nowTime))
        return self.infraed.select_channel_by_number(command)


    def select_channel_by_name(self,command):
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging select_channel_by_name tv time is：  %s"+str(nowTime))
        return self.infraed.select_channel_by_name(command)


    def volume_up(self):
        """Increase volume by one."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging volume_up tv time is：  %s"+str(nowTime))
        return self.infraed.volume_up()


    def volume_down(self):
        """Decrease volume by one."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging volume_down tv time is：  %s"+str(nowTime))
        return self.infraed.volume_down()


    def mute_volume(self, mute):
        """Mute the volume."""

        nowTime = datetime.datetime.now()
        logger_obj.warning("beging mute_volume tv time is"+str(nowTime))
        return  self.infraed.mute_volume(mute)


    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""


    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return None