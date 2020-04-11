from .HuiHeLight import HuiHeLight
from .huiHeSwitch import HuiHeSwitch
from .HuiHeClimate import HuiHeClimate
from .HuiHeMediaPlayer import HuiHeMediaPlayer
from .HuiHeFan import HuiHeFanDevice
from .constant import SWITCH_MODEL,LIGHT_MODEL,CLIMATE_MODEL,MEDIA_PLAYER_MODEL,FAN_MODEL

def get_huihe_device(device_info, api):
    dev_type = device_info["device_type"]
    devices = []
    if dev_type.strip().lower() in LIGHT_MODEL:

        devices.append(HuiHeLight(device_info, api))
    elif dev_type in CLIMATE_MODEL:
        devices.append(HuiHeClimate(device_info, api))
    elif dev_type.strip().lower() in MEDIA_PLAYER_MODEL:
        devices.append(HuiHeMediaPlayer(device_info, api))
    elif dev_type.strip().lower() in  FAN_MODEL:
        devices.append(HuiHeFanDevice(device_info, api))
    # elif dev_type == 'cover':
    #     devices.append(TuyaCover(data, api))
    # elif dev_type == 'lock':
    #     devices.append(TuyaLock(data, api))
    elif dev_type.strip().lower() in SWITCH_MODEL:
        devices.append(HuiHeSwitch(device_info, api))
    return devices



