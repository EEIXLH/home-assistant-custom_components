# -*- coding:utf-8 -*-

from .get_huihe_device  import get_huihe_device
import sqlite3
from .deviceDB import createTable,insertOneDevice,selectAll,selectCodeByEndpointId,deleteOneDevice,updateCodeListByEndpointId
from .sendCode import send_code
from .log import logger_obj
db_path = '.homeassistant/irdevices.db'
AYLA_DEVICE_SERVER = "ads-field.aylanetworks.com"  # 美国开发环境
APPID="huihe-d70b5148-field-us-id"
APPSECRET="huihe-d70b5148-field-us-orxaM7xo-jcuYLzvMKNwofCv9NQ"
TUYACLOUDURL = "https://px1.tuya{}.com"
DEFAULTREGION = 'us'
REFRESHTIME = 60 * 60 * 12

class HuiHeSession:

    username = ''
    password = ''
    countryCode = ''
    bizType = ''
    accessToken = ''
    refreshToken = ''
    expireTime = 0
    devices = []
    test={}
    region = DEFAULTREGION


SESSION = HuiHeSession()


class InfraedApi():


    def init(self,hass):
        self.hass=hass
        self.discover_devices()
        return SESSION.devices


    def poll_devices_update(self):
        return self.discover_devices()


    def discover_devices(self):
        SESSION.devices=[]
        device_list=[]
        # 数据库文件是test.db
        # 如果文件不存在，会自动在当前目录创建:
        conn = sqlite3.connect(db_path)
        conn.text_factory = str
        # 创建一个Cursor:
        cursor = conn.cursor()

        createTable(cursor)
        device_list=selectAll(cursor)
        # 关闭Cursor:
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()
        if device_list!=[]:
           for device in device_list:
               SESSION.devices.extend(get_huihe_device(device, self))
        else:
           pass

        return device_list


    def get_devices_by_type(self, dev_type):
        device_list = []
        for device in SESSION.devices:
            if device.dev_type() == dev_type:
                device_list.append(device)


    def add_new_device(self,device):
        logger_obj.info(" add_new_device：  %s",device)

        conn = sqlite3.connect(db_path)
        conn.text_factory = str
        # 创建一个Cursor:
        cursor = conn.cursor()

        result=insertOneDevice(cursor,device)

        if result==True:
            pass
        else:
            insertOneDevice(cursor, device)
        # 关闭Cursor:
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()

        self.discover_devices()
        return SESSION.devices


    def delete_device(self, dev_id):

        infraed_str = "infraed_"
        num = dev_id.index(infraed_str)
        number = num + 8
        device_id = dev_id[number:]
        logger_obj.info(" delete_device device_id：  %s", device_id)
        conn = sqlite3.connect(db_path)
        conn.text_factory = str
        # 创建一个Cursor:
        cursor = conn.cursor()

        deleteOneDevice(cursor,device_id)

        # 关闭Cursor:
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()

        return


    def modify_device_code(self,device):
        endpointId = str(device["entity_id"])
        key_id = str(device["key_id"])
        irdata = device["pulse"]
        infraed_str="infraed_"
        if infraed_str in endpointId:
            num=endpointId.index(infraed_str)
            number = num + 8
            device_id = endpointId[number:]

        else:
            device_id=endpointId
        logger_obj.info(" modify_device_code device_id：  %s", device_id)
        conn = sqlite3.connect(db_path)
        conn.text_factory = str
        # 创建一个Cursor:
        cursor = conn.cursor()
        rows=selectCodeByEndpointId(cursor,device_id)
        modifyList = []
        for row in rows:
            if row is not None:
                if type(row["keylist"]) == str:

                    keylist = row["keylist"]
                else:
                    keylist = row["keylist"].decode('utf-8')
                jsonList = eval(keylist)
                i = 0
                for codeDate in jsonList:
                    if str(key_id) == str(codeDate['key_id']):
                        i = i + 1
                        codeDate['pulse'] = irdata
                    modifyList.append(codeDate)

                if i == 0:
                    logger_obj.info(" modify_device_code no same key id device_id ")
                    addcode = {}
                    addcode["key_id"] = key_id
                    addcode["pulse"] = irdata
                    modifyList.append(addcode)

        logger_obj.info(" modifyList：  %s",modifyList)
        updateCodeListByEndpointId(cursor, str(modifyList).encode('utf-8'), device_id)

        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()

        self.discover_devices()
        return SESSION.devices


    def get_all_devices(self):
        return SESSION.devices


    def get_device_by_id(self, dev_id):
        for device in SESSION.devices:
            if device.object_id() == dev_id:
                return device
        return None

    def get_code(self, endpointId, keyId):
        code=""
        kfid=""
        codeList=[]
        conn = sqlite3.connect(db_path)
        conn.text_factory = str
        # 创建一个Cursor:
        cursor = conn.cursor()
        rows=selectCodeByEndpointId(cursor,endpointId)
        device_list = []
        for row in rows:
            if row is not None:
                jsonList = []
                if str(endpointId) == str(row['device_id']):
                    kfid = row["kfid"]
                    keylist = row['keylist']
                    jsonList = eval(keylist)
                for codeDate in jsonList:
                    logger_obj.info("get_code codeDate：  %s",codeDate)
                    if str(keyId) == str(codeDate['key_id']):
                        code = codeDate['pulse']
                        codeList = code.split(",")

        # 关闭Cursor:
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()

        return codeList,kfid

    def device_control(self, device_id, keyId, param=None):

        sendResponse = -1
        code,kfid=self.get_code(device_id,keyId)
        if code !=[]:
            sendResponse=send_code(code)

        if sendResponse == True:

            return True
        else:

            return False





    async def ac_control(self, device_id, acValue):
        logger_obj.info("ac_control acValue：  %s",acValue)
        sendResponse=-1
        device={}
        code,kfid=self.get_code(device_id,acValue)
        if kfid=="-1":
            if code != []:
                sendResponse=send_code(code)
            else:
                return False
        else:
            device["entity_id"]=device_id
            device["key_id"]=acValue

            if code !=[]:
                sendResponse=send_code(code)
            else:
                type="GetAcEvent"
                data={
                    "kfid": kfid,
                    "par": acValue
                }
                client = self.hass.data["mqtt_client"]
                response = await client.call_cloud_service(type, data)
                if response["code"] == 0:
                    code=response["data"]["irdata"]
                else:
                    logger_obj.info(" ac_control response error ")
                    code=response["data"]["irdata"]

                if code!=None:
                    codeList = code.split(",")
                    sendResponse=send_code(codeList)
                    device["pulse"]=code
                    self.modify_device_code(device)
                else:
                    return False

        if sendResponse == True:

            return True
        else:

            return False




class iFutureHomeAPIException(Exception):
    pass


