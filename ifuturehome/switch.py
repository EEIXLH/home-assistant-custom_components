"""Support for Huihe switches."""
import datetime
from .log import logger_obj
from . import DATA_HUIHE, HuiheDevice
from . import HUIHE_DISCOVERY_NEW, DATA_HUIHE_DISPATCHERS, DATA_HUIHE_API, DOMAIN as HUIHE_DOMAIN
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchDevice, DOMAIN
# def setup_platform(hass, config, add_entities, discovery_info=None):
#     """Set up Huihe Switch device."""
#     nowTime = datetime.datetime.now()
#     if discovery_info is None:
#         return
#     huihe = hass.data[DATA_HUIHE]
#     dev_ids = discovery_info.get('dev_ids')
#     devices = []
#     for dev_id in dev_ids:
#         device = huihe.get_device_by_id(dev_id)
#         if device is None:
#             continue
#         devices.append(HuiheSwitch(device))
#     add_entities(devices)
#     nowTime = datetime.datetime.now()


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


async def _async_setup_entities(hass, config_entry, async_add_entities, dev_ids):
    huihe = hass.data[DATA_HUIHE][config_entry.entry_id]["data_huihe_api"]
    devices = []
    for dev_id in dev_ids:
        device = huihe.get_device_by_id(dev_id)
        if device is None:
            continue
        devices.append(HuiheSwitch(device))
    async_add_entities(devices)
    dev_ids.clear()


class HuiheSwitch(HuiheDevice, SwitchDevice):
    """Huihe Switch Device."""

    def __init__(self, huihe):
        """Init Huihe switch device."""
        super().__init__(huihe)
        self.entity_id = ENTITY_ID_FORMAT.format(huihe.object_id())


    @property
    def is_on(self):
        """Return true if switch is on."""
        return self.huihe.state()


    def turn_on(self, **kwargs):
        """Turn the switch on."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging turn_on switch time is"+str(nowTime))
        self.huihe.turn_on()


    def turn_off(self, **kwargs):
        """Turn the device off."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging turn_off switch time is"+str(nowTime))
        self.huihe.turn_off()
