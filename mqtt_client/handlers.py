""" 处理mqtt消息 """
from .utils import Utils
from .const import (BOX_SN, TOPIC_DEVICES_GET, TOPIC_CONFIG_SET, TOPIC_SERVICE_CALL, TOPIC_AUTOMATIONS_GET, TOPIC_SYSTEM_RESET, TOPIC_SYSTEM_UPGRADE,
                    TOPIC_AUTOMATIONS_SET, TOPIC_AUTOMATIONS_DELETE, TOPIC_HA_STATUS_GET, TOPIC_FLOW_INIT, TOPIC_FLOW_CONFIG, TOPIC_CONFIG_ENTRIES_GET, TOPIC_CONFIG_ENTRIES_DELETE,
                    SHELL_PATH_UPGRADE, SHELL_PATH_RESET, TOPIC_ENTITY_REGISTRY_LIST, TOPIC_ENTITY_REGISTRY_GET, TOPIC_ENTITY_REGISTRY_UPDATE, TOPIC_ENTITY_REGISTRY_REMOVE, TOPIC_SMARTTHINGS_EVENT,
                    TOPIC_HA_EVENT, TOPIC_DEVICE_REGISTRY_LIST)
from .exception import MqttException
from homeassistant import config_entries, data_entry_flow
from homeassistant.util.decorator import Registry
import homeassistant.config as conf_util
import voluptuous as vol
import homeassistant.loader as loader
import homeassistant.core as ha
from homeassistant.helpers.typing import (HomeAssistantType)
from homeassistant.helpers.entity_registry import async_get_registry
from homeassistant.helpers import config_validation as cv
from homeassistant.const import SERVICE_HOMEASSISTANT_RESTART, CONF_ID, SERVICE_RELOAD
from homeassistant.components.automation import DOMAIN as AUTO_DOMAIN, PLATFORM_SCHEMA
import json
import logging
import os
_LOGGER = logging.getLogger(__name__)

HANDLERS = Registry()


@HANDLERS.register(TOPIC_FLOW_CONFIG)
async def handle_config_flow(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 处理配置流 """
    try:
        payload = json.loads(str(payload, encoding="utf-8"))
        CONFIG_FLOW_SCHEMA = vol.Schema({
            vol.Required('flow_id'): str,
            vol.Optional('data', default={}): dict,
        }, extra=vol.ALLOW_EXTRA)
        valid_payload = CONFIG_FLOW_SCHEMA(payload)
        flow_id = valid_payload['flow_id']
        data = valid_payload['data']
        result = await hass.config_entries.flow.async_configure(flow_id, data)
        client.publish_with_success(
            topic_reply, Utils.prepare_flow_result_json(result))
    except data_entry_flow.UnknownFlow as e:
        _LOGGER.error("Invalid flow specified")
        raise MqttException(MqttException.ERROR_INVALID_FLOW,
                            'Invalid flow specified.' + str(e))


@HANDLERS.register(TOPIC_FLOW_INIT)
async def handle_init_flow(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 初始化配置流 """
    payload = json.loads(str(payload, encoding="utf-8"))

    INIT_FLOW_SCHEMA = vol.Schema({
        vol.Required('handler'): str,
        vol.Optional('source', default=config_entries.SOURCE_USER): str,
        vol.Optional('data'): dict,
    }, extra=vol.ALLOW_EXTRA)
    payload = INIT_FLOW_SCHEMA(payload)
    handler = payload['handler']
    source = payload['source']
    data = None
    if 'data' in payload:
        data = payload['data']
    result = await hass.config_entries.flow.async_init(
        handler, context={"source": source}, data=data
    )
    client.publish_with_success(
        topic_reply, Utils.prepare_flow_result_json(result))


@HANDLERS.register(TOPIC_CONFIG_ENTRIES_GET)
async def handle_get_config_entries(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 获取已集成的配置 """
    results = []
    for entry in hass.config_entries.async_entries():
        handler = config_entries.HANDLERS.get(entry.domain)
        supports_options = (
            # Guard in case handler is no longer registered (custom compnoent etc)
            handler is not None
            # pylint: disable=comparison-with-callable
            and handler.async_get_options_flow != config_entries.ConfigFlow.async_get_options_flow
        )
        results.append(
            {
                "entry_id": entry.entry_id,
                "domain": entry.domain,
                "title": entry.title,
                "source": entry.source,
                "state": entry.state,
                "connection_class": entry.connection_class,
                "supports_options": supports_options,
            }
        )
    client.publish_with_success(topic_reply, results)


@HANDLERS.register(TOPIC_CONFIG_ENTRIES_DELETE)
async def handle_delete_config_entries(hass: HomeAssistantType, topic, topic_reply, payload, client):
    payload = json.loads(str(payload, encoding="utf-8"))

    DELETE_ENTITY_SCHEMA = vol.Schema({
        vol.Required('entry_id'): cv.string
    }, extra=vol.ALLOW_EXTRA)
    data = DELETE_ENTITY_SCHEMA(payload)
    entry_id = data['entry_id']

    try:
        result = await hass.config_entries.async_remove(entry_id)
        client.publish_with_success(topic_reply, result)
    except config_entries.UnknownEntry:
        raise MqttException(MqttException.ERROR_NOT_FOUND,
                            'Invalid entry specified.')


@HANDLERS.register(TOPIC_DEVICE_REGISTRY_LIST)
async def handle_device_registry_list(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 获取所有已经配置的实体 """
    from homeassistant.helpers.device_registry import async_get_registry as async_get_device_registry
    registry = await async_get_device_registry(hass)
    client.publish_with_success(topic_reply, [Utils.device_to_json(
        entry) for entry in registry.devices.values()])


@HANDLERS.register(TOPIC_ENTITY_REGISTRY_LIST)
async def handle_entity_registry_list(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 获取所有已经配置的实体 """
    registry = await async_get_registry(hass)
    client.publish_with_success(topic_reply, [Utils.entry_to_json(
        entry) for entry in registry.entities.values()])


@HANDLERS.register(TOPIC_ENTITY_REGISTRY_GET)
async def handle_entity_registry_get(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 获取所有已经配置的实体 """
    payload = json.loads(str(payload, encoding="utf-8"))
    SCHEMA = vol.Schema({
        vol.Required('entity_id'): cv.entity_id
    }, extra=vol.ALLOW_EXTRA)
    data = SCHEMA(payload)
    entity_id = data['entity_id']

    registry = await async_get_registry(hass)
    entry = registry.entities.get(entity_id)
    if entry is None:
        raise MqttException(MqttException.ERROR_NOT_FOUND,
                            'Entity not found.')
    client.publish_with_success(topic_reply, Utils.entry_to_json(entry))


@HANDLERS.register(TOPIC_ENTITY_REGISTRY_UPDATE)
async def handle_entity_registry_update(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 更新实体 """
    payload = json.loads(str(payload, encoding="utf-8"))
    _LOGGER.error(payload)
    SCHEMA = vol.Schema({
        vol.Required("entity_id"): cv.entity_id,
        # If passed in, we update value. Passing None will remove old value.
        vol.Optional("name"): vol.Any(str, None),
        vol.Optional("disabled_by"): vol.Any("user", None)
    }, extra=vol.ALLOW_EXTRA)
    data = SCHEMA(payload)
    entity_id = data['entity_id']

    registry = await async_get_registry(hass)
    entry = registry.entities.get(entity_id)

    if entry is None:
        raise MqttException(MqttException.ERROR_NOT_FOUND,
                            'Entity not found.')

    changes = {}

    if "name" in data:
        changes["name"] = data["name"]

    if "disabled_by" in data:
        changes["disabled_by"] = data["disabled_by"]

    if changes:
        entry = registry.async_update_entity(entity_id, **changes)

    client.publish_with_success(topic_reply, Utils.entry_to_json(entry))


@HANDLERS.register(TOPIC_ENTITY_REGISTRY_REMOVE)
async def handle_entity_registry_remove(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 移除实体 """
    payload = json.loads(str(payload, encoding="utf-8"))
    SCHEMA = vol.Schema({
        vol.Required('entity_id'): cv.entity_id
    }, extra=vol.ALLOW_EXTRA)
    data = SCHEMA(payload)
    entity_id = data['entity_id']
    registry = await async_get_registry(hass)

    if entity_id not in registry.entities:
        raise MqttException(MqttException.ERROR_NOT_FOUND,
                            'Entity not found.')

    registry.async_remove(entity_id)
    client.publish_with_success(topic_reply, None)


@HANDLERS.register(TOPIC_SYSTEM_RESET)
async def handler_system_reset(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 处理重置请求 """
    import subprocess
    subprocess.Popen(
        ['sh', SHELL_PATH_RESET]
    )
    client.publish_with_success(topic_reply, None)


@HANDLERS.register(TOPIC_SYSTEM_UPGRADE)
async def handler_system_upgrade(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 处理升级请求 """
    import subprocess
    subprocess.Popen(
        ['sh', SHELL_PATH_UPGRADE]
    )
    client.publish_with_success(topic_reply, None)


@HANDLERS.register(TOPIC_HA_STATUS_GET)
async def handle_get_ha_state(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 处理获取盒子详情的请求 """
    pin_code = Utils.get_pin_code(hass)
    failed_components = Utils.get_failed_components(hass)
    config_path = os.path.join(hass.config.config_dir, conf_util.YAML_CONFIG_FILE)
    conf_dict = Utils.read_yaml(config_path)

    sys_configs = Utils.read_kv_config_file('/update/version_info.txt')
    from homeassistant.const import __version__
    from homeassistant.util import get_local_ip
    from .config import config as stage_config

    result = {
        'sn': BOX_SN,
        'ha_ver': __version__,
        'components_ver': stage_config.ver,
        'kernel_firmware': sys_configs.get('kernel_firmware'),
        'release_time': sys_configs.get('release_time'),
        'pinCode': pin_code,
        'failed_components': failed_components,
        'config': conf_dict,
        'network': {
            'local_ip': get_local_ip(),
            'mac_addr': Utils.get_mac()
        }
    }
    client.publish_with_success(topic_reply, result)


@HANDLERS.register(TOPIC_DEVICES_GET)
async def handle_get_devices(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 处理获取设备列表的请求 """
    devices = []
    for state in hass.states.async_all():
        devices.append(state.as_dict())
    client.publish_with_success(topic_reply, devices)


@HANDLERS.register(TOPIC_CONFIG_SET)
async def handle_set_config(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 处理添加配置的请求 """
    # 加载配置文件内容。字典格式
    config_path = os.path.join(hass.config.config_dir, conf_util.YAML_CONFIG_FILE)
    conf_dict = Utils.read_yaml(config_path)

    payload = json.loads(str(payload, encoding="utf-8"))
    SET_CONFIG_SCHEMA = vol.Schema({
        vol.Required('platform'): str,
        vol.Required('enable'): bool,
        # 如果data为空，则赋值为{}
        vol.Optional('data', default={}): dict,
    }, extra=vol.ALLOW_EXTRA)
    # 校验格式
    payload = SET_CONFIG_SCHEMA(payload)

    platform = payload.get("platform")
    enable = payload.get("enable")
    data = payload.get("data")

    try:
        # 检查配置的是否是ha支持的组件
        await loader.async_get_integration(hass, platform)
    except loader.IntegrationNotFound:
        raise MqttException(
                MqttException.ERROR_INTEGRATION_NOT_FOUND, 'Integration not found.')
    
    if (enable == True):
        # if platform in hass.config.components:
        #     raise MqttException(
        #         MqttException.ERROR_COMPONENT_LOADED, 'Component alreadr loaded.')
        if (platform == "xiaomi_aqara"):
            from homeassistant.components.xiaomi_aqara import CONFIG_SCHEMA
            platform_data = {
                "gateways": data.get("gateways")
            }
            # 校验数据schema是否合法
            CONFIG_SCHEMA(platform_data)
            conf_dict["xiaomi_aqara"] = platform_data
        elif (platform == "tuya"):
            from homeassistant.components.tuya import CONFIG_SCHEMA
            # 校验数据schema是否合法
            platform_data = CONFIG_SCHEMA(data)
            username = platform_data.get("username")
            password = platform_data.get("password")
            country_code = platform_data.get("country_code")
            platform = platform_data.get("platform")

            if not Utils.check_tuya_config(username, password, country_code, platform):
                raise MqttException(
                    MqttException.ERROR_INVALID_PARAM, 'invalid tuya config.')
            conf_dict["tuya"] = platform_data
        elif (platform == "homekit"):
            from homeassistant.components.homekit.const import HOMEKIT_FILE
            Utils.remove_file(hass.config.path(HOMEKIT_FILE))
            conf_dict["homekit"] = {
                'name': 'iFutureLife Box'
            }
        elif (platform == "ifuturehome"):
            username = data.get("username")
            password = data.get("password")
            platform = data.get("platform")

            if not Utils.check_hhy_config(username, password):
                raise MqttException(
                    MqttException.ERROR_INVALID_PARAM, 'invalid ifuturehome username or password.')
            conf_dict["ifuturehome"] = {
                "username": data.get("username"),
                "password": data.get("password"),
                "platform": data.get("platform")
            }
        elif (platform == "ring"):
            from homeassistant.components.ring import CONFIG_SCHEMA, DEFAULT_CACHEDB
            platform_data = CONFIG_SCHEMA(data)

            if not Utils.check_ring_config(hass, platform_data.get('username'), platform_data.get('password')):
                raise MqttException(
                    MqttException.ERROR_INVALID_PARAM, 'invlid ring username or password.')
            conf_dict['ring'] = platform_data
            Utils.add_platform_to_category(conf_dict, 'sensor', 'ring')
            Utils.add_platform_to_category(conf_dict, 'binary_sensor', 'ring')
        else:
            # 其他组件不做特殊处理，直接改配置
            conf_dict[platform] = data
        
        client.publish_with_success(topic_reply, None)

        if platform not in hass.config.components:
            import copy
            conf_dict_copy = copy.deepcopy(conf_dict)
            if (platform == "homekit"):
                conf_dict_copy['homekit'].update({
                    'auto_start': False
                })
            
            from homeassistant.setup import async_setup_component, DATA_SETUP
            # 如果已经加载过且失败，需要进行清理
            if platform in hass.data[DATA_SETUP]:
                hass.data[DATA_SETUP].pop(platform)
            task = await async_setup_component(hass, platform, conf_dict_copy)
            if task:
                if (platform == "homekit"):
                    from homeassistant.components.homekit.const import SERVICE_HOMEKIT_START
                    await Utils.async_call_ha_service(hass, "homekit", SERVICE_HOMEKIT_START)
                # 保存yaml
                Utils.save_config(config_path, conf_dict)
                # 兼容小程序，模拟发送ha停止和启动成功事件
                from homeassistant.const import EVENT_HOMEASSISTANT_START
                event_data = {
                    'event_type': EVENT_HOMEASSISTANT_START,
                    'data': {}
                }
                client.publish(TOPIC_HA_EVENT, event_data)
            else:
                event_data = {
                    'event_type': 'component_load_failed',
                    'data': {
                        'domain': platform
                    }
                }
                client.publish(TOPIC_HA_EVENT, event_data)
                # raise MqttException(
                #     MqttException.ERROR_INVALID_PARAM, 'An error occurred while loading the component.')
        else:
            # 保存yaml
            Utils.save_config(config_path, conf_dict)
            # 重启HA以启用配置
            await Utils.async_call_ha_service(hass, ha.DOMAIN, SERVICE_HOMEASSISTANT_RESTART)

    elif (platform in conf_dict):
        # 没有传入enable: true，则从配置文件中删除该组件配置
        if platform not in hass.config.components:
            raise MqttException(
                MqttException.ERROR_COMPONENT_NOT_LOADED, 'Component did not loaded.')

        if platform == 'homekit':
            from homeassistant.components.homekit.const import HOMEKIT_FILE
            Utils.remove_file(hass.config.path(HOMEKIT_FILE))
        elif platform == 'ring':
            Utils.remove_platform_from_category(conf_dict, 'sensor', 'ring')
            Utils.remove_platform_from_category(
                conf_dict, 'binary_sensor', 'ring')
        conf_dict.pop(platform)

        # 保存yaml
        Utils.save_config(config_path, conf_dict)
        client.publish_with_success(topic_reply, None)
        # 重启HA以启用配置
        await Utils.async_call_ha_service(hass, ha.DOMAIN, SERVICE_HOMEASSISTANT_RESTART)
    else:
        # 删除不存在的配置，直接返回
        client.publish_with_success(topic_reply, None)
        return

@HANDLERS.register(TOPIC_SERVICE_CALL)
async def handle_call_service(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 调用盒子的服务 """
    payload = json.loads(str(payload, encoding="utf-8"))
    service = payload.get("service")
    domain = payload.get("domain")
    data = payload.get("data")

    await Utils.async_call_ha_service(hass, domain, service, data)
    client.publish_with_success(topic_reply, None)


@HANDLERS.register(TOPIC_AUTOMATIONS_GET)
async def handle_get_automation(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 获取自动化列表 """
    CONFIG_PATH = 'automations.yaml'
    current = Utils.read_yaml(hass.config.path(CONFIG_PATH))
    if not current:
        current = []
    client.publish_with_success(topic_reply, current)


@HANDLERS.register(TOPIC_AUTOMATIONS_SET)
async def handle_set_automation(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 添加/修改自动化 """
    CONFIG_PATH = 'automations.yaml'
    data = json.loads(str(payload, encoding="utf-8"))
    # 校验数据schema是否合法
    PLATFORM_SCHEMA(data)

    current = Utils.read_yaml(hass.config.path(CONFIG_PATH))
    if not current:
        current = []
    # 根据id来判断是添加还是修改自动化
    config_key = data.get(CONF_ID)
    for index, cur_value in enumerate(current):
        if cur_value[CONF_ID] == config_key:
            current[index] = data
            break
    else:
        # 这是一个新配置的自动化
        current.append(data)
    Utils.write_yaml(hass.config.path(CONFIG_PATH), current)
    await Utils.async_call_ha_service(hass, AUTO_DOMAIN, SERVICE_RELOAD)
    client.publish_with_success(topic_reply, None)


@HANDLERS.register(TOPIC_AUTOMATIONS_DELETE)
async def handle_delete_automation(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 删除自动化 """
    CONFIG_PATH = 'automations.yaml'
    data = json.loads(str(payload, encoding="utf-8"))

    logging.info(json.dumps(data))
    current = Utils.read_yaml(hass.config.path(CONFIG_PATH))
    # 根据id来判断是添加还是修改自动化
    logging.info(json.dumps(current))
    config_key = data.get(CONF_ID)
    # 获取要删除的automation在列表中的索引
    index = next(
        idx for idx, val in enumerate(current)
        if val.get(CONF_ID) == config_key)
    current.pop(index)
    Utils.write_yaml(hass.config.path(CONFIG_PATH), current)
    await Utils.async_call_ha_service(hass, AUTO_DOMAIN, SERVICE_RELOAD)
    client.publish_with_success(topic_reply, None)

@HANDLERS.register(TOPIC_SMARTTHINGS_EVENT)
async def handle_handler_smartthings_event(hass: HomeAssistantType, topic, topic_reply, payload, client):
    """ 监听SmartThings事件 """
    
    data = json.loads(str(payload, encoding="utf-8"))
    domain = "hh_smartthings"
    service = "on_smartthings_event"

    await Utils.async_call_ha_service(hass, domain, service, data)
    # client.publish_with_success(topic_reply, None)
