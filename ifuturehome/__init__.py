"""Support for ifuturehome Smart devices."""
from datetime import timedelta
from .log import get_logger
import voluptuous as vol
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_USERNAME, CONF_PASSWORD, )
from homeassistant.helpers.dispatcher import ( async_dispatcher_connect)
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_COMMAND,
)
from .log import logger_obj
from .constant import SWITCH_OEM_MODEL,LIGHT_OEM_MODEL,HUMIDIFIER_OEM_MODEL,IRDEVICE_OEM_MODEL
from .iFutureHomeapi import iFutureHomeApi
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.dispatcher import async_dispatcher_send
# 缓存监听者
DATA_HUIHE_DISPATCHERS = "huihe_dispatchers"
DATA_HUIHE_TIMER = "huihe_timer"
DOMAIN = 'ifuturehome'
DATA_HUIHE = 'data_huihe'
DATA_HUIHE_API = "data_huihe_api"
# 新设备通知
HUIHE_DISCOVERY_NEW = "huihe_discovery_new_{}"
SIGNAL_DELETE_ENTITY = 'huihe_delete'
SIGNAL_UPDATE_ENTITY = 'huihe_update'

SERVICE_FORCE_UPDATE = 'force_update'
SERVICE_PULL_DEVICES = 'pull_devices'

HUMIDITY_TYPE = ['0001-0401-0001','0001-0401-0002']


# 缓存监听者
DATA_HUIHE_DISPATCHERS = "huihe_dispatchers"
DATA_HUIHE_TIMER = "huihe_timer"

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

HUIHE_TYPE = ['light','switch' ,'climate' ,'media_player']

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_USERNAME): cv.string
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
    hass.data[DOMAIN] = {'entities': {}}
    hass.data[DATA_HUIHE] = {}
    return True

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType, HomeAssistantType

async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    huihe = iFutureHomeApi()
    config = CONFIG_SCHEMA(entry.data)
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    # hass.data[DATA_HUIHE] = huihe
    hass.data[DATA_HUIHE][entry.entry_id] = {
        DATA_HUIHE_API: huihe,
        DATA_HUIHE_DISPATCHERS: []
    }

    huihe.init(username, password)
    hass.data[DOMAIN]["entities"].update({entry.entry_id: {}})
    hass.data[DOMAIN]["entities"][entry.entry_id]["devices"] = []

    async def load_devices(device_list):
        """Load new devices by device_list."""


        print("load_devices device_type_list:",device_list)
        print("devices:", hass.data[DOMAIN]['entities'][entry.entry_id]["devices"])
        device_type_list = {}
        for device in device_list:
            dev_type = device.device_type()

            if (dev_type in HUIHE_TYPE_TO_HA.keys() and  device.object_id() not in hass.data[DOMAIN]['entities'][entry.entry_id]["devices"]):
                ha_type = HUIHE_TYPE_TO_HA[dev_type]
                hass.data[DOMAIN]["entities"][entry.entry_id]["devices"].append(device.object_id())
                if ha_type not in device_type_list:
                    device_type_list[ha_type] = []
                device_type_list[ha_type].append(device.object_id())
        hass.data[DOMAIN]["entities"][entry.entry_id].update({"new_devices": {}})


        for ha_type,dev_ids in device_type_list.items():
            print("dev_ids？？？？:", dev_ids)
            print("ha_type？？？？:", ha_type)
            hass.data[DOMAIN]["entities"][entry.entry_id]["new_devices"][ha_type] = dev_ids


    device_list = huihe.get_all_devices()
    await load_devices(device_list)


    for ha_type in HUIHE_TYPE:
        print("entry-----:", entry)
        print("ha_type-----:", ha_type)
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, ha_type)
        )

    async def poll_devices_update(event_time):
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
        for dev_id in list(hass.data[DOMAIN]["entities"][entry.entry_id]["devices"]):
            oldlist_ids.append(dev_id)
        # logger_obj.warning("oldlist_ids :" + str(oldlist_ids))

        for dev_id in list(hass.data[DOMAIN]['entities'][entry.entry_id]["devices"]):
            if dev_id not in newlist_ids:
                logger_obj.info("SIGNAL_DELETE_ENTITY ha_type,dev_id :" + str(dev_id) )
                hass.data[DOMAIN]["entities"][entry.entry_id]["devices"].remove(dev_id)
                async_dispatcher_send(hass, SIGNAL_DELETE_ENTITY, dev_id)
                from homeassistant.helpers.entity_registry import async_get_registry
                registry = await async_get_registry(hass)
                for entity in list(registry.entities.values()):
                    if "huihe.{}".format(dev_id) == entity.unique_id:
                        registry.async_remove(entity.entity_id)


        await load_devices(device_list)

        for ha_type, dev_ids in hass.data[DOMAIN]["entities"][entry.entry_id]["new_devices"].items():
            async_dispatcher_send(hass, HUIHE_DISCOVERY_NEW.format(ha_type), dev_ids)
            # logger_obj.warning("load_platform ha_type,dev_ids :" +str(ha_type)+" ,"+str(dev_ids))
            # discovery.load_platform(hass, ha_type, DOMAIN, {'dev_ids': dev_ids}, config)


    # 定时拉取设备列表更新
    remove_listener = async_track_time_interval(hass, poll_devices_update, timedelta(minutes=5))
    hass.data[DATA_HUIHE][entry.entry_id].update({DATA_HUIHE_TIMER: remove_listener})
    hass.services.async_register(DOMAIN, SERVICE_PULL_DEVICES, poll_devices_update)


    async def force_update(call):
        """Force all devices to pull data."""
        async_dispatcher_send(hass, SIGNAL_UPDATE_ENTITY)


    hass.services.async_register(DOMAIN, SERVICE_FORCE_UPDATE, force_update)


    async def select_channel_by_number(service):
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
            if (dev_type =="tv" and device.object_id() in hass.data[DOMAIN]['entities'][entry.entry_id]["devices"]):
                logger_obj.debug("select_channel_by_number.get tv device：  %s", str(device))
                type = "number"
                device.select_channel(command,type)


    hass.services.async_register(DOMAIN, 'select_channel_by_number', select_channel_by_number, schema=SERVICE_CHANNEL_SCHEMA_BY_NUMBER)


    async def select_channel_by_name(service):
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
            if (dev_type =="tv" and device.object_id() in hass.data[DOMAIN]['entities'][entry.entry_id]["devices"]):
                logger_obj.debug("select_channel_by_name.get tv device：  %s", str(device))
                type = "name"
                device.select_channel(command,type)


    hass.services.async_register(DOMAIN, 'select_channel_by_name', select_channel_by_name, schema=SERVICE_CHANNEL_SCHEMA_BY_NAME)


    async def set_timer(service):
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
            if (dev_type in HUMIDIFIER_OEM_MODEL and device.object_id() in hass.data[DOMAIN]['entities'][entry.entry_id]["devices"]):
                logger_obj.debug("select_channel_by_name.get humiditfier device", device)
                device.set_timer(command,dev_type)


    hass.services.async_register(DOMAIN, 'set_timer', set_timer, schema=SERVICE_TIMER)


    return True

async def async_unload_entry(hass: HomeAssistantType, entry: ConfigEntry):
    """Unload a config entry."""
    dispatchers = hass.data[DATA_HUIHE][entry.entry_id].get(DATA_HUIHE_DISPATCHERS, [])
    for unsub_dispatcher in dispatchers:
        unsub_dispatcher()

    remove_listener = hass.data[DATA_HUIHE][entry.entry_id].get(DATA_HUIHE_TIMER)
    if remove_listener:
        # _LOGGER.error('取消监听')
        remove_listener()

    import asyncio
    tasks = [
        hass.config_entries.async_forward_entry_unload(entry, component)
        # for component in hass.data[DOMAIN]["entities"][entry.entry_id]
        for component in HUIHE_TYPE_TO_HA.values()
    ]
    hass.data[DOMAIN]["entities"].pop(entry.entry_id, None)
    hass.data[DATA_HUIHE].pop(entry.entry_id, None)
    return all(await asyncio.gather(*tasks))



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
        return self.huihe.update()


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


