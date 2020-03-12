"""Support for ifuturehome Smart devices."""
from datetime import timedelta
from .log import get_logger
import voluptuous as vol
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_USERNAME, CONF_PASSWORD, CONF_PLATFORM)
from homeassistant.helpers import discovery
from homeassistant.helpers.dispatcher import (
    dispatcher_send, async_dispatcher_connect)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_interval
from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_COMMAND,
    CONF_FRIENDLY_NAME,
    CONF_HOST,
    CONF_MAC,
    CONF_SWITCHES,
    CONF_TIMEOUT,
    CONF_TYPE,
    STATE_ON,
)
import datetime
from .log import logger_obj
from .constant import SWITCH_OEM_MODEL,LIGHT_OEM_MODEL,HUMIDIFIER_OEM_MODEL,IRDEVICE_OEM_MODEL



DOMAIN = 'ifuturehome'
DATA_HUIHE = 'data_huihe'

SIGNAL_DELETE_ENTITY = 'huihe_delete'
SIGNAL_UPDATE_ENTITY = 'huihe_update'

SERVICE_FORCE_UPDATE = 'force_update'
SERVICE_PULL_DEVICES = 'pull_devices'

HUMIDITY_TYPE = ['0001-0401-0001','0001-0401-0002']


HUIHE_TYPE_TO_HA = {
    '0001-0201-0001': 'light',
    '0000-0101-0001':'switch' ,
    '0001-0401-0001':'climate' ,
    '0001-0401-0002':'climate' ,
    '0001-0202-0001':'light',
    'light':'light',
    'ac':'climate',
    'tv':'media_player',
}

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Optional(CONF_PLATFORM, default='ifuturehome'): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)


SERVICE_CHANNEL_SCHEMA_BY_NAME= vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): cv.string,
        vol.Required(CONF_COMMAND):cv.string,
    }
)

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
    from .iFutureHomeapi import iFutureHomeApi
    huihe = iFutureHomeApi()
    username = config[DOMAIN][CONF_USERNAME]
    password = config[DOMAIN][CONF_PASSWORD]
    platform = config[DOMAIN][CONF_PLATFORM]
    hass.data[DATA_HUIHE] = huihe
    huihe.init(username, password, platform)
    hass.data[DOMAIN] = {
        'entities': {}
    }


    def load_devices(device_list):
        """Load new devices by device_list."""
        device_type_list = {}
        for device in device_list:
            dev_type = device.device_type()
            if (dev_type in HUIHE_TYPE_TO_HA.keys() and  device.object_id() not in hass.data[DOMAIN]['entities']):
                ha_type = HUIHE_TYPE_TO_HA[dev_type]
                if ha_type not in device_type_list:
                    device_type_list[ha_type] = []
                device_type_list[ha_type].append(device.object_id())
                hass.data[DOMAIN]['entities'][device.object_id()] = None
        for ha_type,dev_ids in device_type_list.items():
            discovery.load_platform(
                hass, ha_type, DOMAIN, {'dev_ids': dev_ids}, config)


    device_list = huihe.get_all_devices()
    load_devices(device_list)


    def poll_devices_update(event_time):
        """Check if accesstoken is expired and pull device list from server."""
        huihe.poll_devices_update()
        device_list = huihe.get_all_devices()
        # load_devices(device_list)
        newlist_ids = []
        oldlist_ids = []
        device_type_list = {}
        for device in device_list:
            newlist_ids.append(device.object_id())
        # logger_obj.warning("newlist_ids :" + str(newlist_ids))
        for dev_id in list(hass.data[DOMAIN]["entities"]):
            oldlist_ids.append(dev_id)
        # logger_obj.warning("oldlist_ids :" + str(oldlist_ids))

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
                        ha_type = HUIHE_TYPE_TO_HA[dev_type]
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


    def select_channel_by_number(service):
        """Handle the service call."""
        params = service.data.copy()
        logger_obj.info("select_channel_by_number.params：  %s", str(params))
        command=params["command"]
        logger_obj.info("select_channel_by_number.command：  %s", command)
        logger_obj.info("select_channel_by_number.command：  %s", command)
        device_list = huihe.get_all_devices()
        for device in device_list:
            dev_type = device.device_type()
            logger_obj.debug("select_channel_by_number.dev_type：  %s",str(dev_type))
            object_id = device.object_id()
            logger_obj.debug("select_channel_by_number.object_id：  %s", str(object_id))
            if (dev_type =="tv" and device.object_id() in hass.data[DOMAIN]['entities']):
                logger_obj.debug("select_channel_by_number.get tv device：  %s", str(device))
                type = "number"
                device.select_channel(command,type)


    hass.services.register(DOMAIN, 'select_channel_by_number', select_channel_by_number, schema=SERVICE_CHANNEL_SCHEMA_BY_NUMBER)


    def select_channel_by_name(service):
        """Handle the service call."""
        params = service.data.copy()
        logger_obj.info("select_channel_by_name.params：  %s", str(params))
        command = params["command"]
        logger_obj.info("select_channel_by_name.command：  %s", str(command))
        device_list = huihe.get_all_devices()
        for device in device_list:
            dev_type = device.device_type()
            logger_obj.debug("select_channel_by_name.dev_type：  %s", str(dev_type))
            object_id = device.object_id()
            logger_obj.debug("select_channel_by_name.object_id：  %s", str(object_id))
            if (dev_type =="tv" and device.object_id() in hass.data[DOMAIN]['entities']):
                logger_obj.debug("select_channel_by_name.get tv device：  %s", str(device))
                type = "name"
                device.select_channel(command,type)


    hass.services.register(DOMAIN, 'select_channel_by_name', select_channel_by_name, schema=SERVICE_CHANNEL_SCHEMA_BY_NAME)


    def set_timer(service):
        """Handle the service call."""
        params = service.data.copy()
        logger_obj.info("set_timer.params", params)
        command = params["command"]
        logger_obj.info("set_timer.command", command)
        device_list = huihe.get_all_devices()
        for device in device_list:
            dev_type = device.device_type()
            logger_obj.debug("set_timer.dev_type", dev_type)
            object_id = device.object_id()
            logger_obj.debug("set_timer.object_id", object_id)
            if (dev_type in HUMIDIFIER_OEM_MODEL and device.object_id() in hass.data[DOMAIN]['entities']):
                logger_obj.debug("select_channel_by_name.get humiditfier device", device)
                device.set_timer(command,dev_type)


    hass.services.register(DOMAIN, 'set_timer', set_timer, schema=SERVICE_TIMER)


    return True





class HuiheDevice(Entity):
    """huihe base device."""

    def __init__(self, huihe):
        """Init huihe devices."""
        self.huihe = huihe


    async def async_added_to_hass(self):
        """Call when entity is added to hass."""
        dev_id = self.huihe.object_id()
        self.hass.data[DOMAIN]['entities'][dev_id] = self.entity_id
        async_dispatcher_connect(
            self.hass, SIGNAL_DELETE_ENTITY, self._delete_callback)
        async_dispatcher_connect(
            self.hass, SIGNAL_UPDATE_ENTITY, self._update_callback)


    @property
    def object_id(self):
        """Return huihe device id."""
        return self.huihe.object_id()


    @property
    def unique_id(self):
        """Return a unique ID."""
        return 'huihe.{}'.format(self.huihe.object_id())


    @property
    def name(self):
        """Return huihe device name."""
        return self.huihe.name()


    @property
    def available(self):
        """Return if the device is available."""
        return self.huihe.available()


    def update(self):
        """Refresh huihe device data."""
        self.huihe.update()


    @property
    def should_poll(self):
        """Return True if entity has to be polled for state.

        False if entity pushes its state to HA.
        """
        # return False
        if self.huihe.get_oem_model() in IRDEVICE_OEM_MODEL:
            return False
        else:
            return True


    @callback
    def _delete_callback(self, dev_id):
        """Remove this entity."""
        if dev_id == self.huihe.object_id():
            logger_obj.info("_delete device :" + str(dev_id))
            self.hass.async_create_task(self.async_remove())


    @callback
    def _update_callback(self):
        """Call update method."""
        self.async_schedule_update_ha_state(True)


