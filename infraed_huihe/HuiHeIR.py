from .HuiHeClimate import HuiHeClimate
from .HuiHeMediaPlayer import HuiHeMediaPlayer
import copy
def HuiHeIR(data, api):
    devices = []
    deviceId=data["dsn"]

    body,code=api.get_IR_device(deviceId)
    for device in body:
        DATA = ""
        DATA = copy.deepcopy(data)
        DATA["subdevice_name"]=device["subdevice_name"]
        DATA["subdevice_id"] = device["subdevice_id"]
        DATA["device_id"] = device["device_id"]
        DATA["irdata_id"] = device["irdata_id"]
        if device["subdevice_typeID"]==2:

            DATA["dev_type"] = "tv"
            devices.append(HuiHeMediaPlayer(DATA, api))
        elif device["subdevice_typeID"] == 5:

            DATA["dev_type"] = "ac"
            devices.append(HuiHeClimate(DATA, api))
        elif device["subdevice_typeID"] == 8:
            pass
        elif device["subdevice_typeID"] == 10:
            pass

    return devices
