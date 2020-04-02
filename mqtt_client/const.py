import os
import logging
_LOGGER = logging.getLogger(__name__)

current_dir = os.path.dirname(__file__)

# HA盒子的序列号
BOX_SN = '12345'
SN_PATH = '/etc/box_sn'
if os.path.isfile(SN_PATH):
    try:
        with open(SN_PATH, 'r') as f:
            BOX_SN = f.readline().strip().strip('\n')
    except:
        _LOGGER.error('Unable to read /etc/box_sn!!!!!!')
else:
    _LOGGER.error('/etc/box_sn not exist!!!!!!')

# SHELL_PATH_UPGRADE = '/Users/mini/.homeassistant/custom_components/test.sh'
SHELL_PATH_UPGRADE = '/update/update_ver.sh'
SHELL_PATH_RESET = '/update/back_factory.sh'

CA_CERTS = current_dir + '/cert/ca.crt'
CERT_FILE = current_dir + '/cert/client.crt'
KEY_FILE = current_dir + '/cert/client.key'

# 上报盒子事件
TOPIC_HA_EVENT = BOX_SN + '/sync/event'
# 上报设备状态
TOPIC_DEVICE_STATE = BOX_SN + '/sync/state/device'
# 上报盒子状态
TOPIC_STATUS = BOX_SN + '/sync/status'

TOPIC_DEVICE_REGISTRY_LIST = 'service/' + BOX_SN + '/rpc/device_registry/list'
# 获取所有已注册的实体
TOPIC_ENTITY_REGISTRY_LIST = 'service/' + BOX_SN + '/rpc/entity_registry/list'
TOPIC_ENTITY_REGISTRY_GET = 'service/' + BOX_SN + '/rpc/entity_registry/get'
TOPIC_ENTITY_REGISTRY_UPDATE = 'service/' + BOX_SN + '/rpc/entity_registry/update'
TOPIC_ENTITY_REGISTRY_REMOVE = 'service/' + BOX_SN + '/rpc/entity_registry/remove'


# 获取盒子状态
TOPIC_HA_STATUS_GET = 'service/' + BOX_SN + '/rpc/state/get'
# 请求获取设备列表
TOPIC_DEVICES_GET = 'service/' + BOX_SN + '/rpc/devices'
# 设备配置更新请求
TOPIC_CONFIG_SET = 'service/' + BOX_SN + '/rpc/config/set'
# 设备控制请求
TOPIC_SERVICE_CALL = 'service/' + BOX_SN + '/rpc/device/control'

# 系统重置
TOPIC_SYSTEM_RESET = 'service/' + BOX_SN + '/rpc/system/reset'
# 系统升级
TOPIC_SYSTEM_UPGRADE = 'service/' + BOX_SN + '/rpc/system/upgrade'


# 获取动态配置列表
TOPIC_CONFIG_ENTRIES_GET = 'service/' + BOX_SN + '/rpc/config_entries/get'
# 删除动态配置
TOPIC_CONFIG_ENTRIES_DELETE = 'service/' + BOX_SN + '/rpc/config_entries/delete'
# 初始化flow
TOPIC_FLOW_INIT = 'service/' + BOX_SN + '/rpc/flow/init'
# 配置flow
TOPIC_FLOW_CONFIG = 'service/' + BOX_SN + '/rpc/flow/config'

# 获取自动化列表
TOPIC_AUTOMATIONS_GET = 'service/' + BOX_SN + '/rpc/automation/get'
# 设置自动化
TOPIC_AUTOMATIONS_SET = 'service/' + BOX_SN + '/rpc/automation/set'
# 删除自动化
TOPIC_AUTOMATIONS_DELETE = 'service/' + BOX_SN + '/rpc/automation/delete'

TOPIC_SMARTTHINGS_EVENT = 'service/' + BOX_SN + '/sync/smart_things/event'
TOPIC_CALL_CLOUD_SERVICE = BOX_SN + '/rpc/call_cloud_service'

SUBSCRIPTIONS = []
SUBSCRIPTIONS.append(TOPIC_HA_STATUS_GET)
SUBSCRIPTIONS.append(TOPIC_DEVICES_GET)
SUBSCRIPTIONS.append(TOPIC_CONFIG_SET)
SUBSCRIPTIONS.append(TOPIC_SYSTEM_RESET)
SUBSCRIPTIONS.append(TOPIC_SYSTEM_UPGRADE)
SUBSCRIPTIONS.append(TOPIC_SERVICE_CALL)
SUBSCRIPTIONS.append(TOPIC_CONFIG_ENTRIES_GET)
SUBSCRIPTIONS.append(TOPIC_CONFIG_ENTRIES_DELETE)
SUBSCRIPTIONS.append(TOPIC_FLOW_INIT)
SUBSCRIPTIONS.append(TOPIC_FLOW_CONFIG)
SUBSCRIPTIONS.append(TOPIC_AUTOMATIONS_GET)
SUBSCRIPTIONS.append(TOPIC_AUTOMATIONS_SET)
SUBSCRIPTIONS.append(TOPIC_AUTOMATIONS_DELETE)
SUBSCRIPTIONS.append(TOPIC_DEVICE_REGISTRY_LIST)
SUBSCRIPTIONS.append(TOPIC_ENTITY_REGISTRY_LIST)
SUBSCRIPTIONS.append(TOPIC_ENTITY_REGISTRY_GET)
SUBSCRIPTIONS.append(TOPIC_ENTITY_REGISTRY_UPDATE)
SUBSCRIPTIONS.append(TOPIC_ENTITY_REGISTRY_REMOVE)
SUBSCRIPTIONS.append(TOPIC_SMARTTHINGS_EVENT)
SUBSCRIPTIONS.append(TOPIC_CALL_CLOUD_SERVICE + "/reply")
