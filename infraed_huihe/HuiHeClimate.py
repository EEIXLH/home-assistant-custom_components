from .base import InfraedDevice
from .constant import SWITCH_MODEL,LIGHT_MODEL,CLIMATE_MODEL,MEDIA_PLAYER_MODEL
from .climateConst import (
    ATTR_HVAC_MODE, HVAC_MODE_COOL, HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT, SUPPORT_FAN_MODE, HVAC_MODE_AUTO, HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE)
from . import const
import logging
import json
_LOGGER = logging.getLogger(__name__)
from .log import logger_obj



class HuiHeClimate(InfraedDevice):


    def temperature_unit(self):
        return const.TEMP_CELSIUS


    # def current_humidity(self):
    #     return 50
    #     if self.data.get('current_humidity') is None:
    #         return None
    #     return self.data.get('current_humidity')
    #
    #
    # def target_humidity(self):
    #     return 65
    #     if self.data.get('target_humidity') is None:
    #         return None
    #     return self.data.get('target_humidity')
    #
    #
    # def target_humidity_step(self):
    #     return 5
    #     if self.data.get('target_humidity') is None:
    #         return None
    #     return 5


    # def preset_mode(self):
    #     """Return hvac operation ie. heat, cool mode.
    #     Need to be one of HVAC_MODE_*."""
    #     return "Standard"
    #     if  self.data.get('mist')==3:
    #             return "High Mist"
    #     elif self.data.get('mist')==2:
    #             return "Medium Mist"
    #     elif self.data.get('mist')==1:
    #             return "Low Mist"
    #     else:
    #             return "Standard"


    def current_operation(self):
        modelType=self.data["modelType"]
        if modelType==0:
                current_operation='cool'
        elif modelType==1:
                current_operation = 'heat'
        elif modelType==2:
                current_operation = 'auto'
        elif modelType==3:
                current_operation = 'fan_only'
        elif modelType==4:
                current_operation = 'dry'
        return current_operation



    def operation_list(self):
        HVAC_MAP = {
            HVAC_MODE_HEAT: 'heat',
            HVAC_MODE_AUTO: 'auto',
            HVAC_MODE_DRY: 'dry',
            HVAC_MODE_FAN_ONLY: 'fan',
            HVAC_MODE_COOL: 'cool',
            HVAC_MODE_OFF: 'off'
        }

        return HVAC_MAP


    def current_temperature(self):
        current_temperature= self.data["curTmp"]
        return current_temperature


    def target_temperature(self):
        target_temperature=self.data["curTmp"]
        return target_temperature


    def target_temperature_step(self):
        return 1




    def current_swing_mode(self):
        """Return the fan setting."""
        swing_mode =self.data["swing"]
        if swing_mode is None:
                pass
        if swing_mode == '0':
                return "vertical"
        elif swing_mode == '1':
                return "vertical"
        elif swing_mode == '2':
                return "vertical"
        elif swing_mode == '3':
                return "horizontal"
        elif swing_mode == '3':
                return "horizontal"
        return swing_mode




    def swing_modes(self):
        """Return the list of available fan modes."""
        swing_modes = "both"
        return swing_modes


    def current_fan_mode(self):
        """Return the fan setting."""
        fan_speed =self.data["curWindSpeed"]
        if fan_speed is None:
                pass
        if fan_speed == 0:
                return 'auto'
        elif fan_speed ==1:
                return 'low'
        elif fan_speed == 2:
                return 'medium'
        elif fan_speed ==3:
                return 'high'
        return fan_speed




    def fan_modes(self):
        """Return the list of available fan modes."""
        fan_list = "auto"
        return fan_list





    def min_temp(self):
        min_temper = 16
        return min_temper



    def max_temp(self):
        max_temper = 30
        return max_temper




    # def min_humidity(self):
    #     return 30
    #
    #
    #
    # def max_humidity(self):
    #     return 95

    def set_swing_mode(self, swing_mode):
        """Set new target swing operation."""
        if swing_mode == "vertical":
                swing=0
        elif swing_mode == "vertical":
                swing=1
        elif swing_mode == "horizontal":
                swing=4
        if self.data["state"] == "on":
            powerValue = "0-"
            endpointId = self.obj_id
            hvac_mode = self.data["modelType"]
            current_temperature = int(self.data["curTmp"])-16
            fan_speed = self.data["curWindSpeed"]
            acValue = powerValue + str(hvac_mode) + '-' + str(current_temperature) + '-' + str(fan_speed) + '-' + str(swing)+'-4'
            self.infraed.ac_control(endpointId, acValue)

            # self.data["mode_list"]['curTmp'] = temperature
        else:
            logger_obj.warning("CLIMATE IS " + str(self.huihe.state()) + ", can not set_swing_mode")

        return


   # def set_preset_mode(self, preset_mode):
      #  """Set new target preset mode."""
      #  self.api.device_control(self.obj_id, 1)
        # if preset_mode=="Standard":
        #     Attributes="workmode"
        #     value = 0
        # elif preset_mode=="Night Light":
        #     Attributes="workmode"
        #     value = 1
        # elif preset_mode=="Sleep":
        #     Attributes = "workmode"
        #     value =2
        # elif preset_mode=="High Mist":
        #     Attributes = "mist"
        #     value =3
        # elif preset_mode=="Medium Mist":
        #     Attributes = "mist"
        #     value =2
        # elif preset_mode=="Low Mist":
        #     Attributes = "mist"
        #     value =1
        #
        # self.api.device_control(self.obj_id,Attributes, value)



    def set_temperature(self, temperature):
        """Set new target temperature."""

        if self.data["state"] == "on":
            powerValue = "0-"
            endpointId = self.obj_id
            hvac_mode = self.data["modelType"]
            current_temperature = int(temperature)-16
            fan_speed = self.data["curWindSpeed"]

            swing = self.data["swing"]
            acValue = powerValue + str(hvac_mode) + '-' + str(current_temperature) + '-' + str(fan_speed) + '-' + str(swing)+'-2'
            self.infraed.ac_control(endpointId, acValue)

            # self.data["mode_list"]['curTmp'] = temperature
        else:
            logger_obj.warning("CLIMATE IS " + str(self.huihe.state()) + ", can not set_temperature")




    # def set_timer (self, command,dev_type):
    #     self.api.device_control(self.obj_id, 1)
    #     # if dev_type == TYPE_HUMI_023:
    #     #     if command in[2,4,6,8,10]:
    #     #         self.api.device_control(self.obj_id, 'timer', command)
    #     #         _LOGGER.debug("erro 023 humidifer timer , timer is " + command)
    #     #     else:
    #     #         pass
    #     #
    #     # else:
    #     #     self.api.device_control(self.obj_id, 'timer', command)


    # def set_humidity(self, humidity):
    #     """Set new target humidity."""
    #     self.api.device_control(self.obj_id, 1)



    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        if self.data["state"] == "on":
            if fan_mode == 'auto':
                fan_speed = 0
            elif fan_mode == 'low':
                fan_speed = 1
            elif fan_mode == 'medium':
                fan_speed = 2
            elif fan_mode == 'high':
                fan_speed = 3

            powerValue = "0-"
            endpointId = self.obj_id
            hvac_mode = self.data["modelType"]
            current_temperature = int(self.data["curTmp"])-16

            swing = self.data["swing"]
            acValue = powerValue+ str(hvac_mode) + '-' + str(current_temperature) + '-' + str(fan_speed) + '-' + str(swing)+'-3'
            self.infraed.ac_control(endpointId, acValue)
            #self.data["mode_list"]['curWindSpeed'] = value
        else:
            logger_obj.warning("CLIMATE IS " + str(self.huihe.state()) + ",set_fan_mode IS " + str(fan_mode))


    def set_hvac_mode(self, hvac_mode):
        """Set new target operation mode."""
        if self.data["state"] == "on":
            if hvac_mode=='cool':
                    hvac_mode=0
            elif hvac_mode=='heat':
                    hvac_mode = 1
            elif hvac_mode=='auto':
                    hvac_mode = 2
            elif hvac_mode=='fan_only':
                    hvac_mode = 3
            elif hvac_mode== 'dry':
                    hvac_mode =4


            powerValue = "0-"
            endpointId = self.obj_id
            # hvac_mode = self.data["modelType"]
            current_temperature = int(self.data["curTmp"])-16
            fan_speed = self.data["curWindSpeed"]
            swing = self.data["swing"]
            acValue = powerValue+ str(hvac_mode) + '-' + str(current_temperature) + '-' + str(fan_speed) + '-' + str(swing)+'-1'
            self.infraed.ac_control(endpointId, acValue)

            #self.data["mode_list"]['modelType'] = modeType
        else:
            logger_obj.warning("CLIMATE IS " + str(self.huihe.state()) + ",set_hvac_mode IS " + str(hvac_mode))




    def support_target_temperature(self):
        return True


    def support_target_temperature_range(self):
            return True


    def support_wind_speed(self):
        return True


    # def support_humidity(self):
    #     return True


    #def support_preset_modes(self):
     #   return None


    def turn_on(self):
        endpointId =self.obj_id
        hvac_mode = self.data["modelType"]
        current_temperature = int(self.data["curTmp"])-16
        fan_speed = self.data["curWindSpeed"]

        swing=self.data["swing"]
        acValue = "0-" + str(hvac_mode) + '-' + str(current_temperature) + '-' + str(fan_speed)+ '-' + str(swing)+'-0'
        self.infraed.ac_control(endpointId, acValue)

        #self.data["state"] = True



    def turn_off(self):
        endpointId = self.obj_id
        hvac_mode = self.data["modelType"]
        current_temperature = int(self.data["curTmp"])-16
        fan_speed = self.data["curWindSpeed"]

        swing = self.data["swing"]
        acValue = "1-" + str(hvac_mode) + '-' + str(current_temperature) + '-' + str(fan_speed) + '-' + str(swing)+'-0'
        self.infraed.ac_control(endpointId, acValue)
        # self.data["state"] = True
