from .base import InfraedDevice
import json
from .mediaPlayerConst import (
    ATTR_APP_ID, ATTR_APP_NAME, ATTR_INPUT_SOURCE, ATTR_INPUT_SOURCE_LIST,
    ATTR_MEDIA_ALBUM_ARTIST, ATTR_MEDIA_ALBUM_NAME, ATTR_MEDIA_ARTIST,
    ATTR_MEDIA_CHANNEL, ATTR_MEDIA_CONTENT_ID, ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_DURATION, ATTR_MEDIA_EPISODE,
    ATTR_MEDIA_PLAYLIST, ATTR_MEDIA_POSITION, ATTR_MEDIA_POSITION_UPDATED_AT,
    ATTR_MEDIA_SEASON, ATTR_MEDIA_SERIES_TITLE,
    ATTR_MEDIA_SHUFFLE, ATTR_MEDIA_TITLE, ATTR_MEDIA_TRACK,
    ATTR_MEDIA_VOLUME_LEVEL, ATTR_MEDIA_VOLUME_MUTED, ATTR_SOUND_MODE,
    ATTR_SOUND_MODE_LIST,SUPPORT_PREVIOUS_TRACK,  SUPPORT_TURN_OFF,SUPPORT_NEXT_TRACK,
    SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_STEP)


SUPPORT_TV = SUPPORT_VOLUME_STEP | SUPPORT_TURN_ON | SUPPORT_VOLUME_SET | \
             SUPPORT_TURN_OFF | SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | SUPPORT_VOLUME_MUTE

ATTR_TO_PROPERTY = [
    ATTR_MEDIA_VOLUME_LEVEL,
    ATTR_MEDIA_VOLUME_MUTED,
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_DURATION,
    ATTR_MEDIA_POSITION,
    ATTR_MEDIA_POSITION_UPDATED_AT,
    ATTR_MEDIA_TITLE,
    ATTR_MEDIA_ARTIST,
    ATTR_MEDIA_ALBUM_NAME,
    ATTR_MEDIA_ALBUM_ARTIST,
    ATTR_MEDIA_TRACK,
    ATTR_MEDIA_SERIES_TITLE,
    ATTR_MEDIA_SEASON,
    ATTR_MEDIA_EPISODE,
    ATTR_MEDIA_CHANNEL,
    ATTR_MEDIA_PLAYLIST,
    ATTR_APP_ID,
    ATTR_APP_NAME,
    ATTR_INPUT_SOURCE,
    ATTR_INPUT_SOURCE_LIST,
    ATTR_SOUND_MODE,
    ATTR_SOUND_MODE_LIST,
    ATTR_MEDIA_SHUFFLE,
]

CACHE_IMAGES = 'images'
CACHE_MAXSIZE = 'maxsize'
CACHE_LOCK = 'lock'


class HuiHeMediaPlayer(InfraedDevice):


    def state(self):
        """State of the player."""
        state = self.state
        if state is None:
            return True
        return state

    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return None


    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return None


    def media_content_type(self):
        """Content type of current playing media."""
        return "MEDIA_TYPE_CHANNEL"
        # return None


    def media_channel(self):
        """Channel currently playing."""
        return None


    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_TV


    def power(self):
        """Turn the media player off."""

        self.api.device_control(self.obj_id, 1)

        return


    def volume_up(self):
        """Increase volume by one."""
        self.api.device_control(self.obj_id, 50)



    def volume_down(self):
        """Decrease volume by one."""

        self.api.device_control(self.obj_id, 51)


    def mute_volume(self, mute):
        """Mute the volume."""
        self.api.device_control(self.obj_id, 106)


    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        raise NotImplementedError()


    def media_previous_track(self):
        """Send previous track command."""
        self.api.device_control(self.obj_id, 44)


    def media_next_track(self):
        """Send next track command."""
        self.api.device_control(self.obj_id, 43)


    def select_channel(self, command, type):
        subdeviceName = self.data.get('subdevice_name')
        endpointId = self.data.get('dsn')
        self.api.changeChannel(type, subdeviceName, command, endpointId, 'ifracmd_to_dev')


    def media_seek(self, position):
        """Send seek command."""
        raise NotImplementedError()


    def select_source(self, source):
        """Select input source."""
        raise NotImplementedError()


    def select_sound_mode(self, sound_mode):
        """Select sound mode."""
        raise NotImplementedError()




