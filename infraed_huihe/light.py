"""Support for the Huihe lights."""
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_COLOR_TEMP, ATTR_HS_COLOR, ENTITY_ID_FORMAT,
    SUPPORT_BRIGHTNESS, SUPPORT_COLOR, SUPPORT_COLOR_TEMP, Light)
from homeassistant.util import color as colorutil

from . import DATA_INFREAD, InfraedDevice
import datetime
from .log import logger_obj
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ENTITY_ID_FORMAT,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_COLOR_TEMP,
    Light,
    DOMAIN
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Huihe light device."""
    if discovery_info is None:
        return
    infraed = hass.data[DATA_INFREAD]
    dev_ids = discovery_info.get('dev_ids')
    print("infraed:",infraed)
    devices = []
    for dev_id in dev_ids:
        device = infraed.get_device_by_id(dev_id)
        if device is None:
            continue
        devices.append(InfraedLight(device))
    add_entities(devices)





class InfraedLight(InfraedDevice, Light):
    """Infraed light device."""

    def __init__(self, infraed):
        """Init infraed light device."""
        super().__init__(infraed)
        self.entity_id = ENTITY_ID_FORMAT.format(infraed.object_id())


    @property
    def brightness(self):
        """Return the brightness of the light."""
        return int(self.infraed.brightness())


    @property
    def hs_color(self):
        """Return the hs_color of the light."""
        return None
        return tuple(map(int, self.infraed.hs_color()))


    @property
    def color_temp(self):
        """Return the color_temp of the light."""
        return None
        # color_temp = int(self.infraed.color_temp())
        # if color_temp is None:
        #     return None
        # return colorutil.color_temperature_kelvin_to_mired(color_temp)


    @property
    def is_on(self):
        """Return true if light is on."""
        return True
        # return self.infraed.state()


    @property
    def min_mireds(self):
        """Return color temperature min mireds."""
        return None
        return colorutil.color_temperature_kelvin_to_mired(
            self.infraed.min_color_temp())


    @property
    def max_mireds(self):
        """Return color temperature max mireds."""
        return colorutil.color_temperature_kelvin_to_mired(
            self.infraed.max_color_temp())


    def turn_on(self, **kwargs):
        """Turn on or control the light."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging set_fan_mode time is" + str(nowTime))

        if (ATTR_BRIGHTNESS not in kwargs
                and ATTR_HS_COLOR not in kwargs
                and ATTR_COLOR_TEMP not in kwargs):
            self.infraed.turn_on()
        if ATTR_BRIGHTNESS in kwargs:
            self.infraed.set_brightness(kwargs[ATTR_BRIGHTNESS])
        if ATTR_HS_COLOR in kwargs:
            self.infraed.set_color(kwargs[ATTR_HS_COLOR])
        if ATTR_COLOR_TEMP in kwargs:
            color_temp = colorutil.color_temperature_mired_to_kelvin(
                kwargs[ATTR_COLOR_TEMP])
            print("color_temp",color_temp)
            self.infraed.set_color_temp(color_temp)


    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""

        nowTime = datetime.datetime.now()
        logger_obj.warning("beging turn_on light time is"+str(nowTime))
        self.infraed.turn_off()


    @property
    def supported_features(self):
        """Flag supported features."""
        supports = SUPPORT_BRIGHTNESS
        if self.infraed.support_color():
            supports = supports | SUPPORT_COLOR
        if self.infraed.support_color_temp():
            supports = supports | SUPPORT_COLOR_TEMP
        return supports
