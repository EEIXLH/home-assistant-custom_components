"""Support for the Tuya climate devices."""
from homeassistant.components.climate import ENTITY_ID_FORMAT, ClimateDevice
from .constant import SWITCH_OEM_MODEL,LIGHT_OEM_MODEL,HUMIDIFIER_OEM_MODEL,IRDEVICE_OEM_MODEL
from .climateConst import (
    HVAC_MODE_AUTO, HVAC_MODE_COOL, HVAC_MODE_FAN_ONLY, HVAC_MODE_HEAT,HVAC_MODE_DRY,HVAC_MODES,SUPPORT_SWING_MODE,
    SUPPORT_FAN_MODE, SUPPORT_TARGET_TEMPERATURE, HVAC_MODE_OFF,SUPPORT_TARGET_HUMIDITY,SUPPORT_TARGET_TEMPERATURE_RANGE, FAN_AUTO, FAN_HIGH, FAN_LOW, FAN_MEDIUM, HVAC_MODE_AUTO, HVAC_MODE_COOL,
    HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY, HVAC_MODE_HEAT, HVAC_MODE_OFF,SUPPORT_PRESET_MODE,
    SUPPORT_FAN_MODE, SUPPORT_SWING_MODE, SUPPORT_TARGET_TEMPERATURE,
    SWING_BOTH, SWING_HORIZONTAL, SWING_OFF, SWING_VERTICAL)
from .const import (
    ATTR_TEMPERATURE, PRECISION_WHOLE, TEMP_CELSIUS, TEMP_FAHRENHEIT)
from . import DATA_HUIHE, HuiheDevice,log
import datetime
import time
from .log import logger_obj
SUPPORT_FAN = [FAN_AUTO, FAN_HIGH, FAN_MEDIUM, FAN_LOW]
ATTR_MODE = 'mode'
CONST_MODE_FAN_AUTO = 'auto'
CONST_MODE_FAN_LOW = 'low'
CONST_MODE_FAN_MIDDLE = 'middle'
CONST_MODE_FAN_HIGH = 'high'
CONST_MODE_FAN_OFF = 'off'
SUPPORT_SWING = [SWING_OFF, SWING_HORIZONTAL, SWING_VERTICAL, SWING_BOTH]
CONST_FAN_CMD_MAP = {CONST_MODE_FAN_AUTO:0, CONST_MODE_FAN_LOW:2, CONST_MODE_FAN_MIDDLE:3, CONST_MODE_FAN_HIGH:4, CONST_MODE_FAN_OFF:5}
CONST_CMD_FAN_MAP = {v: k for k, v in CONST_FAN_CMD_MAP.items()}
DEVICE_TYPE = 'climate'

HA_STATE_TO_HUIHE = {
    HVAC_MODE_AUTO: 'auto',
    HVAC_MODE_COOL: 'cold',
    HVAC_MODE_FAN_ONLY: 'wind',
    HVAC_MODE_HEAT: 'hot',
    HVAC_MODE_DRY:"dry"
}

HVAC_MAP = {
    HVAC_MODE_HEAT: 'heat',
    HVAC_MODE_AUTO: 'auto',
    HVAC_MODE_DRY: 'dry',
    HVAC_MODE_FAN_ONLY: 'fan',
    HVAC_MODE_COOL: 'cool',
    HVAC_MODE_OFF: 'off'
}

HUMIDI_MAP = {
    HVAC_MODE_AUTO: 'auto',
    HVAC_MODE_OFF: 'off'
}

HUMIDI_MODE=["Sleep","Standard","Night Light","High Mist","Medium Mist","Low Mist"]

HUIHE_STATE_TO_HA = {value: key for key, value in HA_STATE_TO_HUIHE.items()}


SERVICE_CHANNEL = "channel"

DOMAIN = 'ifuturehome'



def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Tuya Climate devices."""

    if discovery_info is None:
        return
    huihe = hass.data[DATA_HUIHE]
    dev_ids = discovery_info.get('dev_ids')
    devices = []
    for dev_id in dev_ids:
        device = huihe.get_device_by_id(dev_id)
        if device is None:
            continue
        devices.append(HuiheClimateDevice(device))
    add_entities(devices)



class HuiheClimateDevice(HuiheDevice, ClimateDevice):
    """Tuya climate devices,include air conditioner,heater."""

    def __init__(self, huihe):
        """Init climate device."""
        super().__init__(huihe)
        self.entity_id = ENTITY_ID_FORMAT.format(huihe.object_id())
        self.operations = [HVAC_MODE_OFF]
        self._available = True


    @property
    def supported_features(self):
        """Return the list of supported features."""
        supports = 0
        if self.huihe.support_target_temperature():
            supports = supports | SUPPORT_TARGET_TEMPERATURE
        if self.huihe.support_target_temperature_range():
            supports = supports | SUPPORT_TARGET_TEMPERATURE_RANGE
        if self.huihe.support_humidity():
            supports = supports | SUPPORT_TARGET_HUMIDITY
        if self.huihe.support_wind_speed():
            supports = supports | SUPPORT_FAN_MODE
        if self.huihe.support_preset_modes():
            supports = supports | SUPPORT_PRESET_MODE
        return supports


    @property
    def state(self) -> str:
        """Return the current state."""
        return self.hvac_mode


    @property
    def precision(self):
        """Return the precision of the system."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return 5
        else:
            return PRECISION_WHOLE


    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return None
        else:
            unit = self.huihe.temperature_unit()
            if unit == 'FAHRENHEIT':
                return TEMP_FAHRENHEIT
            return TEMP_CELSIUS


    @property
    def hvac_mode(self):
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*.
        """
        if not self.huihe.state():
            return HVAC_MODE_OFF
        else:
            if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
                return "auto"
            else:
                current_hvac_mode = self.huihe.current_operation()
                if current_hvac_mode is None:
                    return None
                return current_hvac_mode


    @property
    def hvac_modes(self):
        """Return the list of available hvac operation modes.
        Need to be a subset of HVAC_MODES."""

        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return list(HUMIDI_MAP)
        else:
            return list(HVAC_MAP)


    @property
    def preset_mode(self):
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*."""

        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:

            current_preset_mode = self.huihe.preset_mode()
            if current_preset_mode is None:
                return None
            return current_preset_mode


    @property
    def preset_modes(self):
        """Return the list of available hvac operation modes.
        Need to be a subset of HUMIDI_MODE."""

        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
             return list(HUMIDI_MODE)
        else:
            return None


    @property
    def target_temperature_low(self) :
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return None
        else:
            return self.huihe.min_temp()


    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach.
        Requires SUPPORT_TARGET_TEMPERATURE_RANGE.
        """
        return self.huihe.max_temp()


    @property
    def current_temperature(self):
        """Return the current temperature."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return None
        else:
            return self.huihe.current_temperature()


    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return None
        else:
            return self.huihe.target_temperature()
            # return 25


    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return None
        else:
            return self.huihe.target_temperature_step()


    @property
    def current_humidity(self):
        """Return the current humidity."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return self.huihe.current_humidity()
        else:
            return None


    @property
    def humidity(self):
        """Return the current humidity."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return self.huihe.target_humidity()
        else:
            return None


    @property
    def target_humidity(self):
        """Return the humidity we try to reach."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:

            return self.huihe.target_humidity()
        else:
            return None


    @property
    def fan_mode(self):
        """Return the fan setting."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return None
        else:
            return self.huihe.current_fan_mode()


    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return None
        else:
            return SUPPORT_FAN


    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging set_temperature time is"+str(nowTime))
        if self.huihe.state() == True:
            if ATTR_TEMPERATURE in kwargs:
                self.huihe.set_temperature(kwargs[ATTR_TEMPERATURE])
        elif self.huihe.state() == False:
            logger_obj.warning("CLIMATE IS " + str(self.huihe.state()) + ", can not set_temperature" )
        time.sleep(1)

        self.async_schedule_update_ha_state()


    def set_humidity(self, humidity):
        """Set new target humidity."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging set_humidity time is"+str(nowTime))
        self.huihe.set_humidity(humidity)


    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging set_fan_mode time is"+str(nowTime))
        if self.huihe.state() == True:
            self.huihe.set_fan_mode(fan_mode)
        elif self.huihe.state() == False:
            logger_obj.warning("CLIMATE IS " + str(self.huihe.state()) + ",set_fan_mode IS " + str(fan_mode))
        time.sleep(1)

        self.async_schedule_update_ha_state()


    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging set_hvac_mode time is"+str(nowTime))
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            if hvac_mode == HVAC_MODE_OFF:
                self.huihe.turn_off()
            else:
                self.huihe.turn_on()
        else:
            if self.huihe.state() == True:
                if hvac_mode == HVAC_MODE_OFF:
                    self.huihe.turn_off()
                elif hvac_mode == HVAC_MODE_AUTO:
                    self.huihe.turn_on()
                else:
                    self.huihe.set_hvac_mode(hvac_mode)

            elif self.huihe.state() == False  :

                if hvac_mode == HVAC_MODE_AUTO:
                    self.huihe.turn_on()
                else:
                    logger_obj.warning("CLIMATE IS " + str(self.huihe.state()) + ",set_hvac_mode IS " + str(hvac_mode))
                    pass
            time.sleep(1)
            self.async_schedule_update_ha_state()


    def set_timer(self, command,dev_type):
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging set_timer time is"+str(nowTime))
        self.huihe.set_timer(command,dev_type)


    def set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging set_preset_mode time is"+str(nowTime))
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            self.huihe.set_preset_mode(preset_mode)


    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return None
        else:
            return self.huihe.min_temp()


    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return None
        else:
            return self.huihe.max_temp()


    @property
    def min_humidity(self):
        """Return the minimum humidity."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return self.huihe.min_humidity()
        else:
            return None


    @property
    def max_humidity(self):
        """Return the maximum humidity."""
        if self.huihe.get_oem_model() in HUMIDIFIER_OEM_MODEL:
            return self.huihe.max_humidity()
        else:
            return None

