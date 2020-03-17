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


    def current_humidity(self):
        return 50
        if self.data.get('current_humidity') is None:
            return None
        return self.data.get('current_humidity')


    def target_humidity(self):
        return 65
        if self.data.get('target_humidity') is None:
            return None
        return self.data.get('target_humidity')


    def target_humidity_step(self):
        return 5
        if self.data.get('target_humidity') is None:
            return None
        return 5


    def preset_mode(self):
        """Return hvac operation ie. heat, cool mode.
        Need to be one of HVAC_MODE_*."""
        return "Standard"
        if self.data.get('state') is None:
            return None
        else:
            if self.data.get('state')==0:
                return "Off"

            elif self.data.get('workmode')==2:
                return "Sleep"
            elif self.data.get('workmode')==1:
                return "Night Light"
            elif self.data.get('workmode')==0:
                if  self.data.get('mist')==3:
                    return "High Mist"
                elif self.data.get('mist')==2:
                    return "Medium Mist"
                elif self.data.get('mist')==1:
                    return "Low Mist"
                else:
                    return "Standard"


    def current_operation(self):
        current_operation = 'auto'
        return current_operation
        if "mode_list" in self.data and "modelType" in self.data["mode_list"]:

            modelType=self.data["mode_list"].get('modelType')
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
        current_temperature=26
        return current_temperature
        if "mode_list" in self.data and "curTmp" in self.data["mode_list"]:
            current_temperature = self.data["mode_list"].get('curTmp')
            if current_temperature is None:
                return None


    def target_temperature(self):
        target_temperature=26
        return target_temperature
        if "mode_list" in self.data and "curTmp" in self.data["mode_list"]:
                target_temperature = self.data["mode_list"].get('curTmp')
                if target_temperature is None:
                    return None



    def target_temperature_step(self):
        return 1


    def current_fan_mode(self):
        """Return the fan setting."""
        fan_speed = 'auto'
        return fan_speed
        if "mode_list" in self.data and "curWindSpeed" in self.data["mode_list"]:
                fan_speed = self.data["mode_list"].get('curWindSpeed')
                if fan_speed is None:
                    return None
                if fan_speed == '0':
                    return 'auto'
                elif fan_speed == '1':
                    return 'low'
                elif fan_speed == '2':
                    return 'medium'
                elif fan_speed == '3':
                    return 'high'




    def fan_modes(self):
        """Return the list of available fan modes."""
        fan_list = "auto"
        return fan_list
        if "mode_list" in self.data and "windSpeedList" in self.data["mode_list"]:
                fan_speed_list = self.data["mode_list"].get('windSpeedList')
                fan_list=[]
                if fan_speed_list is None:
                    pass
                if fan_speed_list == '0':
                    fan_list.append('auto')
                elif fan_speed_list == '1':
                    fan_list.append('low')
                elif fan_speed_list == '2':
                    fan_list.append('medium')
                elif fan_speed_list == '3':
                    fan_list.append('high')




    def min_temp(self):
        min_temper = 16
        return min_temper
        if "mode_list" in self.data and "lowTmp" in self.data["mode_list"]:
                min_temper = self.data["mode_list"].get('lowTmp')
                if min_temper is None:
                    return None
                if min_temper==0:
                    return 17




    def max_temp(self):
        max_temper = 30
        return max_temper
        if "mode_list" in self.data and "highTmp" in self.data["mode_list"]:
                max_temper = self.data["mode_list"].get('highTmp')
                if max_temper is None:
                    return None
                if max_temper==0:
                    return 30




    def min_humidity(self):
        return 30
        if self.data.get('target_humidity') is None:
            return None



    def max_humidity(self):
        return 95
        if self.data.get('target_humidity') is None:
            return None


    def set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        self.api.device_control(self.obj_id, 1)
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

        self.api.device_control(self.obj_id, 1)

        # irdata_id = self.data.get('irdata_id')
        # filename = "{irdata_id}.json"
        # fm = filename.format(irdata_id=irdata_id)
        # with open(fm) as f_obj:
        #     irdatas = json.load(f_obj)
        #
        # if self.data["state"] == True:
        #     irCodes = irdatas["keys"]
        #     fan_speed = self.data["mode_list"].get('curWindSpeed')
        #     hvac_mode = self.data["mode_list"].get('modelType')
        #     acValue = 'M' + str(hvac_mode) + '_T' + str(int(temperature)) + '_S' + str(fan_speed)
        #     for code in irCodes:
        #         if code["fkey"] == acValue:
        #             endpointId = self.data.get('dsn')
        #             self.api.ir_control(endpointId, "ifracmd_to_dev", code)
        #         else:
        #             pass
        #     self.data["mode_list"]['curTmp']=temperature
        # else:
        #     logger_obj.warning("CLIMATE IS " + str(self.huihe.state()) + ", can not set_temperature")


    def set_timer (self, command,dev_type):
        self.api.device_control(self.obj_id, 1)
        # if dev_type == TYPE_HUMI_023:
        #     if command in[2,4,6,8,10]:
        #         self.api.device_control(self.obj_id, 'timer', command)
        #         _LOGGER.debug("erro 023 humidifer timer , timer is " + command)
        #     else:
        #         pass
        #
        # else:
        #     self.api.device_control(self.obj_id, 'timer', command)


    def set_humidity(self, humidity):
        """Set new target humidity."""
        self.api.device_control(self.obj_id, 1)



    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""

        self.api.device_control(self.obj_id, 1)
        # print("fan_mode", fan_mode)
        # value=""
        # irdata_id = self.data.get('irdata_id')
        # filename = "{irdata_id}.json"
        # fm = filename.format(irdata_id=irdata_id)
        # with open(fm) as f_obj:
        #     irdatas = json.load(f_obj)
        # if fan_mode == 'auto':
        #     value = 0
        # elif fan_mode == 'low':
        #     value = 1
        # elif fan_mode == 'medium':
        #     value = 2
        # elif fan_mode == 'high':
        #     value = 3
        #
        # if self.data["state"] == True:
        #     irCodes = irdatas["keys"]
        #     hvac_mode = self.data["mode_list"].get('modelType')
        #     current_temperature = self.data["mode_list"].get('curTmp')
        #     acValue = 'M' + str(hvac_mode) + '_T' +  str(int(current_temperature)) + '_S' + str(value)
        #     for code in irCodes:
        #         if code["fkey"] == acValue:
        #             endpointId = self.data.get('dsn')
        #             self.api.ir_control(endpointId, "ifracmd_to_dev", code)
        #         else:
        #             pass
        #     self.data["mode_list"]['curWindSpeed']=value
        # else:
        #     logger_obj.warning("CLIMATE IS " + str(self.huihe.state()) + ",set_fan_mode IS " + str(fan_mode))


    def set_hvac_mode(self, hvac_mode):
        """Set new target operation mode."""
        self.api.device_control(self.obj_id, 1)
        # endpointId = self.data.get('dsn')
        # irdata_id=self.data.get('irdata_id')
        #
        # filename = "{irdata_id}.json"
        # fm = filename.format(irdata_id=irdata_id)
        # with open(fm) as f_obj:
        #     irdatas = json.load(f_obj)
        # if hvac_mode=='off':
        #
        #     irCodes = irdatas["keys"]
        #     for code in irCodes:
        #         if code["fkey"] == "power_off":
        #             self.api.ir_control(endpointId, "ifracmd_to_dev", code)
        #         else:
        #             pass
        # else:
        #     current_temperature = self.data["mode_list"].get('curTmp')
        #     fan_speed = self.data["mode_list"].get('curWindSpeed')
        #     if hvac_mode=='cool':
        #         modeType=0
        #         acValue = 'M' + str(modeType) + '_T' +  str(int(current_temperature)) + '_S' + str(fan_speed)
        #     elif hvac_mode=='heat':
        #         modeType = 1
        #         acValue = 'M' + str(modeType) + '_T' +  str(int(current_temperature))+ '_S' + str(fan_speed)
        #     elif hvac_mode=='auto':
        #         modeType = 2
        #         acValue = 'M' + str(modeType) + '_T' +  str(int(current_temperature))
        #     elif hvac_mode=='fan_only':
        #         modeType = 3
        #         acValue = 'M' + str(modeType) + '_S' + str(fan_speed)
        #     elif hvac_mode== 'dry':
        #         modeType =4
        #         acValue = 'M' + str(modeType) + '_T' +  str(int(current_temperature))
        #
        #     irCodes = irdatas["keys"]
        #     for code in irCodes:
        #         if code["fkey"] == acValue:
        #             endpointId = self.data.get('dsn')
        #             self.api.ir_control(endpointId, "ifracmd_to_dev", code)
        #         else:
        #             pass
        #
        # self.data["mode_list"]['modelType'] = modeType


    def support_target_temperature(self):
        return True


    def support_target_temperature_range(self):
            return True
            # if self.data["mode_list"].get('modelType') is not None:
            #     return True
            # else:
            #     return False


    def support_wind_speed(self):
        return True


    def support_humidity(self):
        return True


    def support_preset_modes(self):
            return None


    def turn_on(self):
        self.api.device_control(self.obj_id, 1)
        # irdata_id = self.data.get('irdata_id')
        # filename = "{irdata_id}.json"
        # fm = filename.format(irdata_id=irdata_id)
        # with open(fm) as f_obj:
        #     irdatas = json.load(f_obj)
        # irCodes = irdatas["keys"]
        # current_temperature = self.data["mode_list"].get('curTmp')
        # fan_speed = self.data["mode_list"].get('curWindSpeed')
        # hvac_mode=self.data["mode_list"].get('modelType')
        #
        # acValue = 'M' + str(hvac_mode) + '_T' + str(int(current_temperature)) + '_S' + str(fan_speed)
        # for code in irCodes:
        #     if code["fkey"] == acValue:
        #             endpointId = self.data.get('dsn')
        #             self.api.ir_control(endpointId, "ifracmd_to_dev", code)
        #     else:
        #             pass
        #
        # self.data["state"] =True



    def turn_off(self):
        self.api.device_control(self.obj_id, 1)

            # irdata_id = self.data.get('irdata_id')
            # filename = "{irdata_id}.json"
            # fm = filename.format(irdata_id=irdata_id)
            #
            # with open(fm) as f_obj:
            #     irdatas = json.load(f_obj)
            # irCodes=irdatas["keys"]
            #
            # for code in irCodes:
            #     if code["fkey"]=="power_off":
            #         endpointId = self.data.get('dsn')
            #         self.api.ir_control(endpointId, "ifracmd_to_dev", code)
            #     else:
            #         pass
            # self.data["state"] = False
            #
            #
