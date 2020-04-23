from .constant import SWITCH_MODEL,LIGHT_MODEL,CLIMATE_MODEL,MEDIA_PLAYER_MODEL,FAN_MODEL

class InfraedDevice(object):
    def __init__(self, device_info, api):
        self.api = api
        self.data = {}
        self.device_info = device_info
        self.obj_name = device_info.get('device_name')
        self.obj_id = device_info.get('device_id')
        self.dev_type = device_info.get('device_type')
        self.kfid = device_info.get('kfid')
        self.keylist = device_info.get('keylist')
        self.state = "on"
        self.key_id_list = []
        jsonlst=eval(self.keylist)
        for keys in jsonlst:
            key_id = keys["key_id"]
            self.key_id_list.append(key_id)


        if self.dev_type in SWITCH_MODEL:
                self.obj_type = "switch"
        elif self.dev_type in LIGHT_MODEL:
                self.obj_type = "light"
        elif self.dev_type in CLIMATE_MODEL:
                self.state = "off"
                self.obj_type = "climate"
                self.data["modelType"] = 0
                self.data["curTmp"] = 26
                self.data["curWindSpeed"] = 0
                self.data["swing"] = 0
        elif self.dev_type in MEDIA_PLAYER_MODEL:
            self.obj_type = "media_player"
        elif self.dev_type in FAN_MODEL:
            self.obj_type = "fan"
        else:
                pass


    def name(self):
        return self.obj_name

    def state(self):
        return self.state

    def device_type(self):


        return self.dev_type

    def kfid(self):
        return self.kfid

    def keylist(self):
        return self.keylist

    def object_id(self):
        ID = 'infraed_{}'.format(self.obj_id)
        return ID

    def available(self):
        return True




    def update(self):
        """Avoid get cache value after control."""


        return True













