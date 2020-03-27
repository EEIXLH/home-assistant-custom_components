"""Support for the Huihe lights."""
from homeassistant.util import color as colorutil
import datetime
from .log import logger_obj
from . import DATA_HUIHE, HuiheDevice
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
from . import HUIHE_DISCOVERY_NEW, DATA_HUIHE_DISPATCHERS, DATA_HUIHE_API, DOMAIN as HUIHE_DOMAIN
from homeassistant.helpers.dispatcher import async_dispatcher_connect

# def setup_platform(hass, config, add_entities, discovery_info=None):
#     """Set up Huihe light device."""
#     if discovery_info is None:
#         return
#     huihe = hass.data[DATA_HUIHE]
#     dev_ids = discovery_info.get('dev_ids')
#     devices = []
#     for dev_id in dev_ids:
#         device = huihe.get_device_by_id(dev_id)
#         if device is None:
#             continue
#         devices.append(HuiheLight(device))
#     add_entities(devices)

async def async_setup_entry(hass, config_entry, async_add_entities):

    async def async_discover(discovery_dev_ids):
        await _async_setup_entities(hass, config_entry, async_add_entities, discovery_dev_ids)

    # 注册新设备监听
    unsub = async_dispatcher_connect(hass, HUIHE_DISCOVERY_NEW.format(DOMAIN), async_discover)

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
        devices.append(HuiheLight(device))
    async_add_entities(devices)
    dev_ids.clear()


class HuiheLight(HuiheDevice, Light):
    """Huihe light device."""

    def __init__(self, huihe):
        """Init Huihe light device."""
        super().__init__(huihe)
        self.entity_id = ENTITY_ID_FORMAT.format(huihe.object_id())


    @property
    def brightness(self):
        """Return the brightness of the light."""
        return int(self.huihe.brightness())


    @property
    def hs_color(self):
        """Return the hs_color of the light."""
        return tuple(map(int, self.huihe.hs_color()))


    @property
    def color_temp(self):
        """Return the color_temp of the light."""
        color_temp = int(self.huihe.color_temp())
        if color_temp is None:
            return None
        return colorutil.color_temperature_kelvin_to_mired(color_temp)


    @property
    def is_on(self):
        """Return true if light is on."""
        return self.huihe.state()


    @property
    def min_mireds(self):
        """Return color temperature min mireds."""
        return colorutil.color_temperature_kelvin_to_mired(
            self.huihe.min_color_temp())


    @property
    def max_mireds(self):
        """Return color temperature max mireds."""
        return colorutil.color_temperature_kelvin_to_mired(
            self.huihe.max_color_temp())


    def turn_on(self, **kwargs):
        """Turn on or control the light."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging set_fan_mode time is" + str(nowTime))

        if (ATTR_BRIGHTNESS not in kwargs
                and ATTR_HS_COLOR not in kwargs
                and ATTR_COLOR_TEMP not in kwargs):
            self.huihe.turn_on()
        if ATTR_BRIGHTNESS in kwargs:
            self.huihe.set_brightness(kwargs[ATTR_BRIGHTNESS])
        if ATTR_HS_COLOR in kwargs:
            self.huihe.set_color(kwargs[ATTR_HS_COLOR])
        if ATTR_COLOR_TEMP in kwargs:
            color_temp = colorutil.color_temperature_mired_to_kelvin(
                kwargs[ATTR_COLOR_TEMP])
            print("color_temp",color_temp)
            self.huihe.set_color_temp(color_temp)


    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""

        nowTime = datetime.datetime.now()
        logger_obj.warning("beging turn_on light time is"+str(nowTime))
        self.huihe.turn_off()


    @property
    def supported_features(self):
        """Flag supported features."""
        supports = SUPPORT_BRIGHTNESS
        if self.huihe.support_color():
            supports = supports | SUPPORT_COLOR
        if self.huihe.support_color_temp():
            supports = supports | SUPPORT_COLOR_TEMP
        return supports
