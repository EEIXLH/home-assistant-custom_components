import yaml
import json
import os
from homeassistant.util.yaml import load_yaml, dump
from homeassistant.helpers.typing import HomeAssistantType
import logging

class Utils:
    @staticmethod
    def json_serial(obj):
        """ 支持datetime转json """
        import datetime
        if isinstance(obj, datetime.datetime):
            return int(round(obj.timestamp() * 1000))
        raise TypeError('Not sure how to serialize %s' % (obj,))

    @staticmethod
    def save_config(config_path: str, conf_dict: dict):
        """ 将字典保存到配置文件 """
        # 防止这些配置跑到configuration.yaml来
        conf_dict['group'] = None
        conf_dict['automation'] = None
        conf_dict['script'] = None

        str_data = yaml.safe_dump(conf_dict)
        str_data = str_data.replace(
            "group: null", "group: !include groups.yaml")
        str_data = str_data.replace(
            "automation: null", "automation: !include automations.yaml")
        str_data = str_data.replace(
            "script: null", "script: !include scripts.yaml")
        print(config_path)
        print(str_data)
        try:
            with open(config_path, 'wt') as config_file:
                config_file.write(str_data)
        except IOError:
            print("Unable to create default configuration file", config_path)

    @staticmethod
    def remove_platform_from_category(conf_dict: dict, category: str, platform: str):
        """ 
            从品类中删除指定配置
            eg:从sensor删除platform为ring的配置
        """
        category_config = conf_dict.get(category, [])
        for platform_config in category_config:
            if platform_config.get('platform') == platform:
                category_config.remove(platform_config)

    @staticmethod
    def add_platform_to_category(conf_dict: dict, category: str, platform: str):
        """ 
            在品类中增加指定配置
            eg:从sensor增加platform为ring的配置
        """
        category_config: list = conf_dict.get(category, [])
        for platform_config in category_config:
            if platform_config.get('platform') == platform:
                return
        category_config.append({
            'platform': platform
        })
        conf_dict[category] = category_config

    @staticmethod
    def read_yaml(path):
        """Read YAML helper."""
        if not os.path.isfile(path):
            return None

        return load_yaml(path)

    @staticmethod
    def write_yaml(path, data):
        """Write YAML helper."""
        # Do it before opening file. If dump causes error it will now not
        # truncate the file.
        data = dump(data)
        with open(path, 'w', encoding='utf-8') as outfile:
            outfile.write(data)

    @staticmethod
    def remove_file(file_path):
        """ 删除文件，避免因文件不存在而报错 """
        try:
            os.remove(file_path)
        except Exception:
            pass

    @staticmethod
    def get_pin_code(hass: HomeAssistantType):
        """ 从通知组件获取homekit的pin code """
        if not hass.data['persistent_notification']:
            return
        notifications = hass.data['persistent_notification']['notifications']
        if notifications == {} or notifications == None:
            return
        notification_hk = notifications.get('persistent_notification.4663548')
        if notification_hk is None:
            return
        message = notification_hk['message']
        arr = message.split('### ')
        if len(arr) < 1:
            return
        pin_code = arr[1]
        return pin_code

    @staticmethod
    def get_failed_components(hass: HomeAssistantType):
        """ 获取加载失败的组件列表 """
        from homeassistant.config import DATA_PERSISTENT_ERRORS
        errors = hass.data.get(DATA_PERSISTENT_ERRORS)
        if errors is None:
            errors = hass.data[DATA_PERSISTENT_ERRORS] = {}

        failed_components = list()

        for name, link in errors.items():
            failed_components.append(name)

        return failed_components

    @staticmethod
    def check_tuya_config(username: str, password: str, country_code: str, platform: str):
        """ 检查涂鸦配置是否正确 """
        from tuyaha import TuyaApi
        tuya = TuyaApi()
        tuya.init(username, password, country_code, platform)
        try:
            tuya.init(username, password, country_code, platform)
            return True
        except Exception:
            return False

    @staticmethod
    def check_hhy_config(username: str, password: str):
        """ 检查iFutureHome配置是否正确 """
        import requests
        AYLA_DEVICE_SERVER = "ads-field.aylanetworks.com"  # 美国开发环境
        APPID = "huihe-d70b5148-field-us-id"
        APPSECRET = "huihe-d70b5148-field-us-orxaM7xo-jcuYLzvMKNwofCv9NQ"

        url = "https://" + AYLA_DEVICE_SERVER + "/users/sign_in.json"
        headers = {'Content-Type': "application/json"}
        data = {"user": {"email": username,
                         "password": password,
                         "application": {"app_id": APPID,
                                         "app_secret": APPSECRET}}}

        try:
            response = requests.request(
                "POST", url, data=json.dumps(data), headers=headers, timeout=6)
            response_json = response.json()

            if response_json.get('error') is not None:
                message = response_json.get('error')
                print('发生错误', message)
                return False
            return True
        except Exception as e:
            print(e)

    @staticmethod
    def check_ring_config(hass: HomeAssistantType, username: str, password: str):
        """ 检查ring账号是否正确 """
        from ring_doorbell import Ring
        from homeassistant.components.ring import DEFAULT_CACHEDB

        cache = hass.config.path(DEFAULT_CACHEDB)
        ring = Ring(username=username, password=password, cache_file=cache)
        if ring.is_connected:
            return True

    @staticmethod
    def read_kv_config_file(file_path):
        """ 
        读取键值对配置文件
        ver=0.0.3 
        """
        result = {}

        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as f:
                    lines = f.read().splitlines()
                    for line in lines:
                        i = line.find('=')
                        if i > 0:
                            k = line[0:i].strip()
                            v = line[i + 1:len(line)].strip()
                            result[k] = v
            except:
                print('Unable to read ' + file_path)
        else:
            print(file_path + ' not exist!!!!!!')
        return result

    @staticmethod
    def prepare_flow_result_json(result):
        """ 转化flow处理数据为json """
        from homeassistant import config_entries, data_entry_flow

        if result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY:
            data = result.copy()
            data["result"] = data["result"].entry_id
            data.pop("data")
            return data
        if result["type"] != data_entry_flow.RESULT_TYPE_FORM:
            return result

        import voluptuous_serialize
        data = result.copy()
        schema = data["data_schema"]
        if schema is None:
            data["data_schema"] = []
        else:
            data["data_schema"] = voluptuous_serialize.convert(schema)
        return data

    @staticmethod
    def entry_to_json(entry):
        """Convert entry to API format."""
        return {
            "config_entry_id": entry.config_entry_id,
            "device_id": entry.device_id,
            "disabled_by": entry.disabled_by,
            "entity_id": entry.entity_id,
            "name": entry.name,
            "platform": entry.platform,
        }

    @staticmethod
    def device_to_json(entry):
        """Convert entry to API format."""
        return {
            "config_entries": list(entry.config_entries),
            "connections": list(entry.connections),
            "manufacturer": entry.manufacturer,
            "model": entry.model,
            "name": entry.name,
            "sw_version": entry.sw_version,
            "id": entry.id,
            "via_device_id": entry.via_device_id,
            "area_id": entry.area_id,
            "name_by_user": entry.name_by_user,
        }

    @staticmethod
    def get_mac():
        """ 获取本机mac地址 """
        from uuid import getnode as get_mac
        mac = get_mac()
        # print(hex(mac))
        # print(':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2)))
        return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

    @staticmethod
    async def async_call_ha_service(hass: HomeAssistantType, domain: str, service: str, service_data=None):
        from homeassistant.core import DOMAIN as HASS_DOMAIN, Context
        blocking = True
        if hass.services.has_service(domain, service):
            await hass.services.async_call(
                domain=domain,
                service=service,
                service_data=service_data,
                blocking=blocking)
        else:
            logging.error('Unable to find service %s/%s', domain, service)
