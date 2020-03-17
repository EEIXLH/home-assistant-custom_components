from .huiHeLight import HuiHeLight
from .huiHeSwitch import HuiHeSwitch
from .HuiHeClimate import HuiHeClimate
from .HuiHeMediaPlayer import HuiHeMediaPlayer
from .constant import SWITCH_MODEL,LIGHT_MODEL,CLIMATE_MODEL,MEDIA_PLAYER_MODEL

def get_huihe_device(device_info, api):
    dev_type = device_info["device_type"]
    devices = []
    if dev_type.strip().lower() in LIGHT_MODEL:
        print("get_huihe_device light dev_type:",dev_type)
        devices.append(HuiHeLight(device_info, api))
    elif dev_type in CLIMATE_MODEL:
        devices.append(HuiHeClimate(device_info, api))
    elif dev_type.strip().lower() in MEDIA_PLAYER_MODEL:
        devices.append(HuiHeMediaPlayer(device_info, api))
    # elif dev_type == 'fan':
    #     devices.append(TuyaFanDevice(data, api))
    # elif dev_type == 'cover':
    #     devices.append(TuyaCover(data, api))
    # elif dev_type == 'lock':
    #     devices.append(TuyaLock(data, api))
    # elif dev_type in SWITCH_OEM_MODEL:
    #     devices.append(HuiHeSwitch(data, api))
    return devices



