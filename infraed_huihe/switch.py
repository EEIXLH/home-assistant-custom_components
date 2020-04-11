"""Support for Huihe switches."""
from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchDevice
import datetime
from .log import logger_obj
from . import DATA_INFREAD, InfraedDevice

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Huihe Switch device."""
    if discovery_info is None:
        return
    huihe = hass.data[DATA_INFREAD]
    dev_ids = discovery_info.get('dev_ids')
    devices = []
    for dev_id in dev_ids:
        device = huihe.get_device_by_id(dev_id)
        if device is None:
            continue
        devices.append(HuiheSwitch(device))
    add_entities(devices)


class HuiheSwitch(InfraedDevice, SwitchDevice):
    """Huihe Switch Device."""

    def __init__(self, infraed):
        """Init infraed light device."""
        super().__init__(infraed)
        self.entity_id = ENTITY_ID_FORMAT.format(infraed.object_id())


    @property
    def is_on(self):
        """Return true if switch is on."""
        if self.infraed.state == "on":

            return True
        else:
            return False


    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self.infraed.turn_on()


    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.infraed.turn_off()
