"""Support for ifuturehome Smart devices."""
from datetime import timedelta
from .log import get_logger
import voluptuous as vol
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.helpers.dispatcher import (
    dispatcher_send, async_dispatcher_connect)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_interval
from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_COMMAND,
    CONF_DEVICE,
    CONF_HOST,
    CONF_MAC,
    CONF_SWITCHES,
    CONF_TIMEOUT,
    CONF_TYPE,
    STATE_ON,
)
import datetime
from .log import logger_obj
from .constant import SWITCH_MODEL,LIGHT_MODEL,MEDIA_PLAYER_MODEL,MEDIA_PLAYER_MODEL
from .learnCode import learn_code,stop_learn
from .sendCode import send_code
from .judgeProcess import judgeprocess
DOMAIN = 'infraed_huihe'
DATA_INFREAD = 'data_infraed'
processname="mode2"
SIGNAL_DELETE_ENTITY = 'infraed_delete'
SIGNAL_UPDATE_ENTITY = 'infraed_update'

SERVICE_FORCE_UPDATE = 'force_update'
SERVICE_PULL_DEVICES = 'pull_devices'

HUMIDITY_TYPE = ['0001-0401-0001','0001-0401-0002']


INFREAD_TYPE_TO_HA = {
    'light': 'light',
    '0000-0101-0001':'switch' ,
    '0001-0401-0001':'climate' ,
    '0001-0401-0002':'climate' ,
    '0001-0202-0001':'light',
    'light':'light',
    'ac':'climate',
    'tv':'media_player',
}


SERVICE_CHANNEL_SCHEMA_BY_NAME= vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): cv.string,
        vol.Required(CONF_COMMAND):cv.string,
    }
)



SERVICE_ADD_NEW_DEVICE= vol.Schema({
    'device_name': str,
    'device_type': str,
    vol.Optional('kfid', default="-1"): str,
    'keylist': list
})


SERVICE_STAR_LEARNING_CODE= vol.Schema({
vol.Optional('timeout', default=20): int
})

SERVICE_MODIFY_DEVICE_CODE= vol.Schema({
    'device_name': str,
    'device_type': str,
    'keylist': list
})


SERVICE_SEND_LEARNING_CODE= vol.Schema({
    'pulse': str
})


SERVICE_CONTROLLING_DEVICE=vol.Schema({
    'entity_id': str,
    'action': str
})



SERVICE_MODIFY_DEVICE_CODE= vol.Schema({
    'entity_id': str,
    'key_id': str,
    'pulse': str
})


SERVICE_DELETE_DEVICE= vol.Schema({
    'entity_id': str
})


SERVICE_CHANNEL_SCHEMA_BY_NUMBER= vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): cv.string,
        vol.Required(CONF_COMMAND): vol.Coerce(int),
    }
)

SERVICE_TIMER= vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): cv.string,
        vol.Required(CONF_COMMAND): vol.All(vol.Coerce(int), vol.Clamp(min=1, max=25))
    }
)

def setup(hass, config):
    """Set up ifuturehome Component."""
    logger_obj.info("beging setup ifuturehome")
    from .infraedapi import InfraedApi
    infraed = InfraedApi()
    print("infraedinfraed:",infraed)
    hass.data[DATA_INFREAD] = infraed
    infraed.init()
    hass.data[DOMAIN] = {
        'entities': {}
    }


    def load_devices(device_list):
        """Load new devices by device_list."""
        #print("########1", device_list)
        device_type_list = {}
        for device in device_list:

            dev_type = device.device_type()

            if (dev_type in INFREAD_TYPE_TO_HA.keys() and  device.object_id() not in hass.data[DOMAIN]['entities']):
                ha_type = INFREAD_TYPE_TO_HA[dev_type]
                if ha_type not in device_type_list:
                    device_type_list[ha_type] = []
                device_type_list[ha_type].append(device.object_id())
                hass.data[DOMAIN]['entities'][device.object_id()] = None

        for ha_type,dev_ids in device_type_list.items():
            discovery.load_platform(
                hass, ha_type, DOMAIN, {'dev_ids': dev_ids}, config)


    device_list = infraed.get_all_devices()
    load_devices(device_list)


    def poll_devices_update(event_time):
        """Check if accesstoken is expired and pull device list from server."""
        infraed.poll_devices_update()
        device_list = infraed.get_all_devices()
        newlist_ids = []
        oldlist_ids = []
        device_type_list = {}

        entities = hass.data[DOMAIN]['entities']

        for device in device_list:
            newlist_ids.append(device.object_id())
        # logger_obj.warning("newlist_ids :" + str(newlist_ids))
        for dev_id in list(hass.data[DOMAIN]["entities"]):
            oldlist_ids.append(dev_id)
        # logger_obj.warning("oldlist_ids :" + str(oldlist_ids))

        #logger_obj.info("poll_devices_update dev_id :" + str(dev_id))
        for dev_id in list(hass.data[DOMAIN]['entities']):
            if dev_id not in newlist_ids:
                logger_obj.info("SIGNAL_DELETE_ENTITY ha_type,dev_id :" + str(dev_id) )
                dispatcher_send(hass, SIGNAL_DELETE_ENTITY, dev_id)
                hass.data[DOMAIN]['entities'].pop(dev_id)



        for obj_id in newlist_ids:
            if obj_id not in oldlist_ids:
                for device in device_list:
                    if obj_id == device.object_id():
                        dev_type=device.dev_type
                        ha_type = INFREAD_TYPE_TO_HA[dev_type]
                        if ha_type not in device_type_list:
                            device_type_list[ha_type] = []

                        device_type_list[ha_type].append(device.object_id())
                        hass.data[DOMAIN]['entities'][device.object_id()] = None
        for ha_type, dev_ids in device_type_list.items():
            logger_obj.warning("load_platform ha_type,dev_ids :" +str(ha_type)+" ,"+str(dev_ids))
            discovery.load_platform(hass, ha_type, DOMAIN, {'dev_ids': dev_ids}, config)

    track_time_interval(hass, poll_devices_update, timedelta(minutes=5))
    hass.services.register(DOMAIN, SERVICE_PULL_DEVICES, poll_devices_update)


    def force_update(call):
        """Force all devices to pull data."""
        dispatcher_send(hass, SIGNAL_UPDATE_ENTITY)
    hass.services.register(DOMAIN, SERVICE_FORCE_UPDATE, force_update)


    # OK
    def add_new_device(service):
        """Handle the service call."""
        params = service.data.copy()
        device_list = infraed.add_new_device(params)
        load_devices(device_list)
    hass.services.register(DOMAIN, 'add_new_device', add_new_device, schema=SERVICE_ADD_NEW_DEVICE)

    # OK？？
    def controlling_device(service):
        """Handle the service call."""

        params = service.data.copy()
        endpointId = params['entity_id']
        action = params['action']

        keyId = 0
        if action == "light.brightness_increase":
            keyId = 2202
        elif action == "light.brightness_decrease":
            keyId = 2207
        else:
            pass
        print("keyId:", keyId)
        infraed_str = "infraed_"
        num = endpointId.index(infraed_str)
        print("num:", num)
        number = num + 8
        device_id = endpointId[number:]
        print("device_id:", device_id)
        #更新对应的设备属性暂未实现
        # sendResponse=infraed.device_control(device_id, keyId)
        # if sendResponse == True:
        #     self.state = "off"
        #
        # return

    hass.services.register(DOMAIN, 'controlling_device', controlling_device, schema=SERVICE_CONTROLLING_DEVICE)

    # OK
    def modify_device_code(service):
        """Handle the service call."""
        params = service.data.copy()
        infraed.modify_device_code(params)
    hass.services.register(DOMAIN, 'modify_device_code', modify_device_code, schema=SERVICE_MODIFY_DEVICE_CODE)


    # OK
    def start_learning_code(service):
        """Handle the service call."""
        if judgeprocess(processname) == True:
            return False
        else:
            params = service.data.copy()
            timeout = params["timeout"]

            learnCode = learn_code(timeout)
            sendDate = {}

            print("--------------finish learning code-------------- ")

            if learnCode == []:
                print("hass.bus.fire('send_learning_code_event', learnCode) is null")
            else:
                try:
                    strDate = ','.join(learnCode)
                    sendDate["pulse"] = strDate
                    print("send_learning_code_event strDate:", sendDate)
                    hass.bus.fire("send_learning_code_event", sendDate)
                except:
                    print("hass.bus.fire('send_learning_code_event', learnCode) is erro")
                    pass

        return True
    hass.services.register(DOMAIN, 'start_learning_code', start_learning_code, schema=SERVICE_STAR_LEARNING_CODE)


    # OK
    def stop_learning_code(call):
        """Handle the service call."""
        print("--------------beging stop_learning_code-------------- ")
        stop_learn()
        print("--------------finish stop_learning_code-------------- ")
        return
    hass.services.register(DOMAIN, 'stop_learning_code', stop_learning_code)


    # OK
    def send_learning_code(service):
        """Handle the service call."""

        print("--------------beging send_learning_code-------------- ")
        params = service.data.copy()
        codeList=params["pulse"]
        code=codeList.split(",")
        send_code(code)

        print("--------------finish send_learning_code-------------- ")
    hass.services.register(DOMAIN, 'send_learning_code', send_learning_code, schema=SERVICE_SEND_LEARNING_CODE)


    # OK
    def delete_device(service):
        """Handle the service call."""

        print("--------------beging delete_device-------------- ")
        params = service.data.copy()
        entity_id=params["entity_id"]
        infraed.delete_device(entity_id)
        dispatcher_send(hass, SIGNAL_DELETE_ENTITY, entity_id)
        hass.data[DOMAIN]['entities'].pop(entity_id)

        print("--------------finish delete_device-------------- ")
    hass.services.register(DOMAIN, 'delete_device', delete_device, schema=SERVICE_DELETE_DEVICE)

    return True





class InfraedDevice(Entity):
    """infraed base device."""

    def __init__(self, infraed):
        """Init infraed devices."""
        self.infraed = infraed


    async def async_added_to_hass(self):
        """Call when entity is added to hass."""
        dev_id = self.infraed.object_id()
        self.hass.data[DOMAIN]['entities'][dev_id] = self.entity_id
        async_dispatcher_connect(
            self.hass, SIGNAL_DELETE_ENTITY, self._delete_callback)
        async_dispatcher_connect(
            self.hass, SIGNAL_UPDATE_ENTITY, self._update_callback)


    @property
    def object_id(self):
        """Return infraed device id."""
        #print("object_id:", self.infraed.object_id())
        return self.infraed.object_id()


    @property
    def unique_id(self):
        """Return a unique ID."""
        unique_id='infraed.{}'.format(self.infraed.object_id())
        #print("unique_id:",unique_id)
        return unique_id


    @property
    def name(self):
        """Return infraed device name."""

        return self.infraed.name()


    @property
    def available(self):
        """Return if the device is available."""
        return self.infraed.available()


    def update(self):
        """Refresh infraed device data."""
        return self.infraed.update()


    @property
    def should_poll(self):
        """Return True if entity has to be polled for state.

        False if entity pushes its state to HA.
        """
        return False
        # if self.infraed.get_oem_model() in IRDEVICE_OEM_MODEL:
        #     return False
        # else:
        #     return True


    @callback
    def _delete_callback(self, dev_id):
        """Remove this entity."""
        if dev_id == self.infraed.object_id():
            logger_obj.info("_delete device :" + str(dev_id))
            self.hass.async_create_task(self.async_remove())


    @callback
    def _update_callback(self):
        """Call update method."""
        self.async_schedule_update_ha_state(True)


