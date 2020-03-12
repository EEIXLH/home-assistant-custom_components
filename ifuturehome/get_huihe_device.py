from .huiHeLight import HuiHeLight
from .huiHeSwitch import HuiHeSwitch
from .HuiHeIR import HuiHeIR
from .HuiHeClimate import HuiHeClimate
from .constant import SWITCH_OEM_MODEL,LIGHT_OEM_MODEL,HUMIDIFIER_OEM_MODEL,IRDEVICE_OEM_MODEL

def get_huihe_device(data, api):
    dev_type = data["device"]["oem_model"]
    devices = []
    data=data["device"]
    if dev_type in LIGHT_OEM_MODEL:
        devices.append(HuiHeLight(data, api))
    elif dev_type in HUMIDIFIER_OEM_MODEL:
        devices.append(HuiHeClimate(data, api))
    elif dev_type in IRDEVICE_OEM_MODEL:
        devis_list = HuiHeIR(data, api)
        for device in devis_list:
            devices.append(device)
    # elif dev_type == 'fan':
    #     devices.append(TuyaFanDevice(data, api))
    # elif dev_type == 'cover':
    #     devices.append(TuyaCover(data, api))
    # elif dev_type == 'lock':
    #     devices.append(TuyaLock(data, api))
    elif dev_type in SWITCH_OEM_MODEL:
        devices.append(HuiHeSwitch(data, api))
    return devices



