import time
from .constant import SWITCH_OEM_MODEL,LIGHT_OEM_MODEL,HUMIDIFIER_OEM_MODEL,IRDEVICE_OEM_MODEL
import requests
import json
from .log import logger_obj
import datetime
import time

class InfraedDevice(object):
    def __init__(self, device_info, api):

        self.api = api
        self.device_info = device_info
        self.obj_name = device_info.get('device_name')
        self.obj_id = device_info.get('device_id')
        self.dev_type = device_info.get('device_type')
        self.kfid = device_info.get('kfid')
        self.keylist = device_info.get('keylist')
        self.state = True
        # propertyData = self.api.retrieves_properties(self.obj_id)

        # for propertyData in propertyData:
        #     if "state" in propertyData:
        #         self.data["state"] = propertyData.get('state')
        #     elif "brightness" in propertyData:
        #         self.data["brightness"] = propertyData.get('brightness')
        #     elif "color_temp" in propertyData:
        #         self.data["color_temp"] = propertyData.get('color_temp')
        #     elif "target_humidity" in propertyData:
        #         self.data["target_humidity"] = propertyData.get('target_humidity')
        #         self.data["humidity"] = propertyData.get('target_humidity')
        #     elif "current_humidity" in propertyData:
        #         self.data["current_humidity"] = propertyData.get('current_humidity')
        #     elif "workmode" in propertyData:
        #         self.data["workmode"] = propertyData.get('workmode')
        #     elif "mist" in propertyData:
        #         self.data["mist"] = propertyData.get('mist')
        #     else:
        #         pass
        # if data.get('oem_model') in IRDEVICE_OEM_MODEL:
        #     self.dev_type = data.get('dev_type')
        #     self.obj_id = data.get('subdevice_id')
        #     self.subdevice_typeID = data.get('subdevice_typeID')
        #     self.dsn = data.get('dsn')
        #     self.obj_type = "IR"
        #     self.obj_name = data.get('subdevice_name')
        #     self.irdata_id = data.get('irdata_id')
        #     irdata_id = self.irdata_id
        #     if self.data["dev_type"] == "ac":
        #         deviceId = self.dsn
        #         subdeviceName = self.data.get('subdevice_name')
        #         acData, code = self.api.getACStateInfo(deviceId, subdeviceName)
        #         if acData.get("state") == 0:
        #             self.data["state"] = True
        #         else:
        #             self.data["state"] = False
        #         self.data["mode_list"] = acData.get("mode_list")
        #         irdatas,code=self.api.getIrCode(irdata_id)
        #         if code == 200 or code == 201:
        #             filename = "{irdata_id}.json"
        #             fm=filename.format(irdata_id=irdata_id)
        #             with open(fm, 'w') as file_obj:json.dump(irdatas, file_obj)
        #         else:
        #             pass
        #     else:
        #         self.data["state"] =None
        #         irdatas,code = self.api.getIrCode(irdata_id)
        #         if code == 200 or code == 201:
        #             filename = "{irdata_id}.json"
        #             fm = filename.format(irdata_id=irdata_id)
        #             with open(fm, 'w') as file_obj:
        #                 json.dump(irdatas, file_obj)
        #             pass
        #         else:
        #             pass

        # else:

        if self.dev_type in SWITCH_OEM_MODEL:
                self.obj_type = "switch"
        elif self.dev_type in LIGHT_OEM_MODEL:
                self.obj_type = "light"
        elif self.dev_type in HUMIDIFIER_OEM_MODEL:
                self.obj_type = "climate"
        else:
                pass




    def name(self):

        print("self.obj_name:::",self.obj_name)
        return self.obj_name

    def state(self):
        return True

    def device_type(self):


        return self.dev_type

    def kfid(self):
        return self.kfid

    def keylist(self):
        return self.keylist

    def object_id(self):
        ID = 'infraed#{}'.format(self.obj_id)
        return ID

    def available(self):
        return True




    def update(self):
        """Avoid get cache value after control."""

        # logger_obj.debug("pass update obj_id : %s", self.obj_id)
        # deviceId = self.obj_id
        #
        #
        # if self.data.get('oem_model') in IRDEVICE_OEM_MODEL:
        #     if self.data["dev_type"] == "ac":
        #         logger_obj.debug("update ac")
        #         deviceId = self.dsn
        #         from .infraedapi import iFutureHomeApi
        #         huihe = iFutureHomeApi()
        #         body, code = huihe.get_IR_device(deviceId)
        #         for device in body:
        #             if device["subdevice_id"]==self.obj_id:
        #                 self.obj_name=device["subdevice_name"]
        #             else:
        #                 pass
        #
        #         subdeviceName =self.obj_name
        #         acData, code = self.api.getACStateInfo(deviceId, subdeviceName)
        #         logger_obj.debug("acData：  %s ",acData)
        #         if acData.get("state") == 0:
        #             self.data["state"] = True
        #         else:
        #             self.data["state"] = False
        #         self.data["mode_list"] = acData.get("mode_list")
        #     else:
        #         deviceId = self.dsn
        #         from .infraedapi import iFutureHomeApi
        #         huihe = iFutureHomeApi()
        #         body, code = huihe.get_IR_device(deviceId)
        #         for device in body:
        #             if device["subdevice_id"] == self.obj_id:
        #                 self.obj_name = device["subdevice_name"]
        #             else:
        #                 pass
        #
        # else:
        #     # pass
        #     # deviceId = self.obj_id
        #
        #
        #
        #     nowTime = datetime.datetime.now()
        #     logger_obj.debug("beging update time is：  %s" + str(nowTime))
        #     propertyData = self.api.retrieves_properties(deviceId)
        #     for propertyData in propertyData:
        #         if "state" in propertyData:
        #             self.data["state"] = propertyData.get('state')
        #         elif "brightness" in propertyData:
        #             self.data["brightness"] = propertyData.get('brightness')
        #         elif "color_temp" in propertyData:
        #             self.data["color_temp"] = propertyData.get('color_temp')
        #         elif "target_humidity" in propertyData:
        #             self.data["target_humidity"] = propertyData.get('target_humidity')
        #             self.data["humidity"] = propertyData.get('target_humidity')
        #         elif "current_humidity" in propertyData:
        #             self.data["current_humidity"] = propertyData.get('current_humidity')
        #         elif "workmode" in propertyData:
        #             self.data["workmode"] = propertyData.get('workmode')
        #         elif "mist" in propertyData:
        #             self.data["mist"] = propertyData.get('mist')
        #         else:
        #             pass
        # nowTime = datetime.datetime.now()
        return True













