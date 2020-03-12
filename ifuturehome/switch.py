"""Support for Huihe switches."""
from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchDevice
import datetime
from .log import logger_obj
from . import DATA_HUIHE, HuiheDevice

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Huihe Switch device."""
    nowTime = datetime.datetime.now()
    if discovery_info is None:
        return
    huihe = hass.data[DATA_HUIHE]
    dev_ids = discovery_info.get('dev_ids')
    devices = []
    for dev_id in dev_ids:
        device = huihe.get_device_by_id(dev_id)
        if device is None:
            continue
        devices.append(HuiheSwitch(device))
    add_entities(devices)
    nowTime = datetime.datetime.now()


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
