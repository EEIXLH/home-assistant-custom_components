""" MQTT agent """
import paho.mqtt.client as mqtt
from paho.mqtt.matcher import MQTTMatcher
import json
import logging
import ssl
import voluptuous as vol
import asyncio

from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.event import async_track_state_change
from homeassistant.const import SERVICE_HOMEASSISTANT_RESTART, MATCH_ALL, EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP, EVENT_HOMEASSISTANT_CLOSE, EVENT_PLATFORM_DISCOVERED
from homeassistant.config_entries import EVENT_FLOW_DISCOVERED
from homeassistant import config_entries

from .utils import Utils
from .const import BOX_SN, SUBSCRIPTIONS, TOPIC_DEVICE_STATE, TOPIC_HA_EVENT, TOPIC_CALL_CLOUD_SERVICE, TOPIC_STATUS
from .handlers import HANDLERS
from .exception import MqttException
from .config import config as stage_config

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistantType, config):
    client = MqttClient(hass)

    hass.data["mqtt_client"] = client

    async def async_entity_state_listener(changed_entity, old_state, new_state):
        if new_state is None:
            client.publish(TOPIC_DEVICE_STATE, {})
        else:
            client.publish(TOPIC_DEVICE_STATE, new_state.as_dict())

    # 监听设备属性变化
    async_track_state_change(hass, MATCH_ALL, async_entity_state_listener)

    async def on_event(event):
        """Receive Homeassistant Event."""
        # _LOGGER.error("收到事件消息 " + event.event_type)
        data = {
            'event_type': event.event_type,
            'data': event.data,
            # 'origin': event.origin,
            'time_fired': event.time_fired
            # 'context': event.context
        }
        if (event.event_type == EVENT_HOMEASSISTANT_START):
            client.publish(TOPIC_HA_EVENT, data)
        elif (event.event_type == EVENT_HOMEASSISTANT_STOP):
            client.publish(TOPIC_HA_EVENT, data)
            await client._disconnect()
        elif (event.event_type == EVENT_HOMEASSISTANT_CLOSE):
            client.publish(TOPIC_HA_EVENT, data)

    # 监听ha事件
    hass.bus.async_listen(MATCH_ALL, on_event)
    return True


class MqttClient():
    def __init__(self, hass: HomeAssistantType):
        self.hass = hass
        self.connected = False
        self.client = mqtt.Client(client_id=BOX_SN)
        self.client.will_set(TOPIC_STATUS, payload=json.dumps({
            "status": "disconnected"
        }), qos=0, retain=True)
        self.client.on_connect = self.on_connect_callback
        self.client.on_disconnect = self.on_disconnect_callback
        self.client.on_message = self.on_message_callback
        self._connect()
        self.rpc_id = 0
        self.rpc_queue = []

    def publish_with_success(self, topic, data):
        """Publish Mqtt Message."""
        payload = {
            'code': 0,
            'data': data
        }
        self.client.publish(topic, json.dumps(
            payload, default=Utils.json_serial), 0)

    def publish(self, topic, payload=None, qos=0, retain=False):
        """Publish Mqtt Message."""
        self.client.publish(topic, payload=json.dumps(
            payload, default=Utils.json_serial), qos=qos, retain=retain)

    async def call_cloud_service(self, type, data):
        payload = {
            "type": type,
            "data": data,
            "id": self.rpc_id
        }
        self.publish(TOPIC_CALL_CLOUD_SERVICE, payload)
        f = asyncio.Future()
        rpc_req = {
            "id": payload["id"],
            "task": f
        }
        _LOGGER.debug('call_cloud_service, type: %s, id: %s', type, self.rpc_id)

        self.rpc_queue.append(rpc_req)
        self.rpc_id += 1
        try:
            await asyncio.wait_for(f, 20)
        except Exception as err:
            _LOGGER.error('call_cloud_service error occured, type: %s, id: %s', type, self.rpc_id)
            raise err
        self.rpc_queue.remove(rpc_req)
        return f.result()

    async def handler_rpc_response(self, msg):
        payload = json.loads(str(msg.payload, encoding="utf-8"))
        RESPONSE_SCHEMA = vol.Schema({
            vol.Required('code'): int,
            vol.Required('id'): int,
            # 如果data为空，则赋值为{}
            vol.Optional('data'): object
        }, extra=vol.ALLOW_EXTRA)
        # 校验格式
        payload = RESPONSE_SCHEMA(payload)
        id = payload.get("id")
        code = payload.get("code")
        data = payload.get("data")
        _LOGGER.debug('call_cloud_service response, id: %s, code: %s', id, code)
        for req in self.rpc_queue:
            if req["id"] == id:
                task = req["task"]
                if not task.cancelled():
                    task.set_result(payload)
                    task.done()

    def _connect(self):
        self._connecting_task = self.hass.async_create_task(self._re_connect())

    async def _re_connect(self):
        try:
            # ssl支持
            if stage_config.TLS:
                from .const import CA_CERTS, CERT_FILE, KEY_FILE
                self.client.tls_set(CA_CERTS, CERT_FILE, KEY_FILE, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
            # client.username_pw_set("mint", "se7en7777777")

            result = self.client.connect(
                stage_config.BROKER, stage_config.PORT, stage_config.KEEP_ALIVE)
            self.client.loop_start()

            if result != 0:
                _LOGGER.error("Failed to connect: %s",
                              mqtt.error_string(result))
                _LOGGER.error(result)
        except Exception:
            _LOGGER.error("mqtt_client init failed:")
            self._connect()

    async def _disconnect(self):
        self.publish(TOPIC_STATUS, {
            "status": "disconnected"
        }, qos=0, retain=True)
        self.connected = False
        self.client.disconnect()

    def on_connect_callback(self, client, userdata, flags, rc):
        # on_connect()可以在重连成功后再次订阅topic
        self.connected = True
        _LOGGER.info("Paho connected with result code "+str(rc))
        for subscription in SUBSCRIPTIONS:
            client.subscribe(subscription)
        self.publish(TOPIC_STATUS, {
            "status": "connected"
        }, qos=0, retain=True)
        # 要去服务端检查SmartApp是否已配置/已卸载，暂未通过验证，暂时屏蔽
        self.hass.async_create_task(self.async_on_connect_callback(client, userdata, flags, rc))

    async def async_on_connect_callback(self, client, userdata, flags, rc):
        cloud_platforms = await self.call_cloud_service("GetCloudEnabledPlatforms", None)
        local_platforms = self.hass.config_entries.async_domains()
        _LOGGER.debug(cloud_platforms)
        _LOGGER.debug(local_platforms)

        for platform in cloud_platforms:
            if platform not in local_platforms:
                result = await self.hass.config_entries.flow.async_init(platform, context={"source": config_entries.SOURCE_IMPORT})
                _LOGGER.debug(result)

        DOMAIN_SMARTTHINGS = "hh_smartthings"
        if DOMAIN_SMARTTHINGS not in cloud_platforms and DOMAIN_SMARTTHINGS in local_platforms:
            entries = self.hass.config_entries.async_entries(DOMAIN_SMARTTHINGS)
            for entry in entries:
                try:
                    result = await self.hass.config_entries.async_remove(entry.entry_id)
                except config_entries.UnknownEntry:
                    _LOGGER.error('Invalid entry specified.' + entry.entry_id)

    def on_disconnect_callback(self, client, userdata, rc):
        _LOGGER.info("Paho disconnect callback "+str(rc))

    # The callback for when a PUBLISH message is received from the server.
    def on_message_callback(self, client, userdata, msg):
        self.hass.async_create_task(self.async_handler_message(msg))

    async def async_handler_message(self, msg):
        topic = msg.topic

        if topic == TOPIC_CALL_CLOUD_SERVICE + "/reply":
            await self.handler_rpc_response(msg)
            return

        topic_reply = topic + '/reply'
        _LOGGER.info(msg.topic)
        funct_ref = HANDLERS.get(topic)
        if funct_ref:
            try:
                await funct_ref(self.hass, topic, topic_reply, msg.payload, self)
            except MqttException as e:
                payload = {
                    'code': e.code,
                    'errMsg': str(e)
                }
                self.publish(topic_reply, payload)
            except json.decoder.JSONDecodeError as e:
                import traceback
                traceback.print_exc(e)
                payload = {
                    'code': MqttException.ERROR_INVALID_DATA_FORMAT,
                    'errMsg': str(e)
                }
                self.publish(topic_reply, payload)
            except ValueError as e:
                msg = 'Invalid JSON field...' + str(e)
                payload = {
                    'code': MqttException.ERROR_UNKNOWN,
                    'errMsg': msg
                }
                logging.error(msg)
                self.publish(topic_reply, payload)
            except vol.Invalid as e:
                msg = 'data format invalid...' + str(e)
                payload = {
                    'code': MqttException.ERROR_INVALID_DATA_FORMAT,
                    'errMsg': msg
                }
                logging.error(msg)
                self.publish(topic_reply, payload)
            except Exception as error:
                msg = str(error)
                payload = {
                    'code': MqttException.ERROR_UNKNOWN,
                    'errMsg': msg
                }
                logging.error(msg)
                self.publish(topic_reply, payload)
        else:
            _LOGGER.warning("Unsupported topic received: %s", topic)
