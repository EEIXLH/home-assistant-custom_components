"""Support for Infraed fans."""
from homeassistant.components.fan import (
    ENTITY_ID_FORMAT,
    SUPPORT_OSCILLATE,
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.const import STATE_OFF
from . import DATA_INFREAD, InfraedDevice
import time

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Infraed fan platform."""
    if discovery_info is None:
        return
    infraed = hass.data[DATA_INFREAD]
    dev_ids = discovery_info.get('dev_ids')
    devices = []
    for dev_id in dev_ids:
        device = infraed.get_device_by_id(dev_id)
        if device is None:
            continue
        devices.append(InfraedFanDevice(device))
    add_entities(devices)


class InfraedFanDevice(InfraedDevice, FanEntity):
    """Infraed fan devices."""

    def __init__(self, infraed):
        """Init infraed light device."""
        super().__init__(infraed)
        self.entity_id = ENTITY_ID_FORMAT.format(infraed.object_id())

    def set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if speed == STATE_OFF:
            self.turn_off()
        else:
            self.infraed.set_speed(speed)

    def turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn on the fan."""
        if speed is not None:
            self.set_speed(speed)
        else:
            self.infraed.turn_off()
            time.sleep(2)
            self.async_schedule_update_ha_state()

    def turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        self.infraed.turn_off()
        time.sleep(2)
        self.async_schedule_update_ha_state()

    def oscillate(self, oscillating) -> None:
        """Oscillate the fan."""
        self.infraed.oscillate(oscillating)

    @property
    def oscillating(self):
        """Return current oscillating status."""
        if self.supported_features & SUPPORT_OSCILLATE == 0:
            return None
        if self.speed == STATE_OFF:
            return False
        return self.infraed.oscillating()

    @property
    def is_on(self):
        """Return true if the entity is on."""
        if self.infraed.state == "on":

            return True
        else:
            return False

    @property
    def speed(self) -> str:
        """Return the current speed."""
        if self.is_on:
            return 'on'
            return self.infraed.speed()
        return STATE_OFF

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return self.infraed.speed_list()

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        supports = SUPPORT_SET_SPEED
        if self.infraed.support_oscillate():
            supports = supports | SUPPORT_OSCILLATE
        return supports
