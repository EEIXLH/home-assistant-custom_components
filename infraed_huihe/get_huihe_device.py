from .huiHeLight import HuiHeLight
from .huiHeSwitch import HuiHeSwitch
from .HuiHeIR import HuiHeIR
from .HuiHeClimate import HuiHeClimate
from .constant import SWITCH_OEM_MODEL,LIGHT_OEM_MODEL,HUMIDIFIER_OEM_MODEL,IRDEVICE_OEM_MODEL

def get_huihe_device(device_info, api):
    dev_type = device_info["device_type"]
    devices = []
    if dev_type.strip().lower() in LIGHT_OEM_MODEL:
        print("get_huihe_device light dev_type:",dev_type)
        devices.append(HuiHeLight(device_info, api))
    # elif dev_type in HUMIDIFIER_OEM_MODEL:
    #     devices.append(HuiHeClimate(device_info,device_id, api))
    # elif dev_type in IRDEVICE_OEM_MODEL:
    #     devis_list = HuiHeIR(device_info,device_id, api)
    #     for device in devis_list:
    #         devices.append(device)
    # elif dev_type == 'fan':
    #     devices.append(TuyaFanDevice(data, api))
    # elif dev_type == 'cover':
    #     devices.append(TuyaCover(data, api))
    # elif dev_type == 'lock':
    #     devices.append(TuyaLock(data, api))
    # elif dev_type in SWITCH_OEM_MODEL:
    #     devices.append(HuiHeSwitch(data, api))
    return devices



