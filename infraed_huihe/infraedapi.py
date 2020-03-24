# -*- coding:utf-8 -*-
import collections
# import sys
#
#
# sys.setdefaultencode('utf8')
import json
import requests
import time
import gzip
from .get_huihe_device  import get_huihe_device
import datetime
import sys
AYLA_DEVICE_SERVER = "ads-field.aylanetworks.com"  # 美国开发环境
APPID="huihe-d70b5148-field-us-id"
APPSECRET="huihe-d70b5148-field-us-orxaM7xo-jcuYLzvMKNwofCv9NQ"
TUYACLOUDURL = "https://px1.tuya{}.com"
DEFAULTREGION = 'us'
import sqlite3
REFRESHTIME = 60 * 60 * 12

from .log import logger_obj
from .deviceDB import createTable,insertOneDevice,selectAll,selectCodeByEndpointId,deleteOneDevice,updateCodeListByEndpointId
from .sendCode import send_code
db_path = 'irdevices.db'


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


class InfraedApi:


    def init(self):

        self.discover_devices()
        return SESSION.devices


    def poll_devices_update(self):
        return self.discover_devices()


    def discover_devices(self):
        SESSION.devices=[]
        device_list=[]
        print("coming discover_devices")
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
        #print("SESSION.devices----:", SESSION.devices)

        return device_list


    def get_devices_by_type(self, dev_type):
        device_list = []
        for device in SESSION.devices:
            if device.dev_type() == dev_type:
                device_list.append(device)


    def add_new_device(self,device):
        print("add_new_device:", device)

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
        print("num:", num)
        number = num + 8
        device_id = dev_id[number:]
        print("device_id:", device_id)
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
            print("num:", num)
            number = num + 8
            device_id = endpointId[number:]

        else:
            device_id=endpointId
        print("device_id:", device_id)

        conn = sqlite3.connect(db_path)
        conn.text_factory = str
        # 创建一个Cursor:
        cursor = conn.cursor()
        rows=selectCodeByEndpointId(cursor,device_id)
        modifyList=[]
        for row in rows:
            if row is not None:
                if type(row[4]) == str:

                    keylist = row[4]
                else:
                    keylist = row[4].decode('utf-8')
                jsonList = eval(keylist)
                i=0
                for codeDate in jsonList:
                    if key_id == codeDate['key_id']:
                        print("key_id---:", key_id)
                        i = i + 1
                        codeDate['pulse'] = irdata
                    modifyList.append(codeDate)

                if i == 0:
                    print("no same key id")
                    addcode = {}
                    addcode["key_id"] = key_id
                    addcode["pulse"] = irdata
                    modifyList.append(addcode)
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
        print("endpointId",endpointId)
        code=""
        codeList=[]
        conn = sqlite3.connect(db_path)
        conn.text_factory = str
        # 创建一个Cursor:
        cursor = conn.cursor()
        rows=selectCodeByEndpointId(cursor,endpointId)
        device_list = []
        for row in rows:
            if row is not None:
                kfid = row[3]
                keylist = row[4].decode('utf-8')
                jsonList = eval(keylist)
                for codeDate in jsonList:
                    if str(keyId) == codeDate['key_id']:
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

        print("device_control code:", code)
        if code !=[]:
            sendResponse=send_code(code)
        # if param is None:
        #     param = {}
        # nowTime = datetime.datetime.now()
        # logger_obj.warning("beging control device time is"+str(nowTime))

        if sendResponse == True:

            return True
        else:

            return False


    # def get_ac_code(self, endpointId, acValue):
    #     print("endpointId",endpointId)
    #     code=""
    #     codeList=[]
    #     conn = sqlite3.connect(db_path)
    #     conn.text_factory = str
    #     # 创建一个Cursor:
    #     cursor = conn.cursor()
    #     rows=selectCodeByEndpointId(cursor,endpointId)
    #     device_list = []
    #     for row in rows:
    #         if row is not None:
    #             kfid= row[3]
    #             keylist = row[4].decode('utf-8')
    #             jsonList = eval(keylist)
    #             if kfid==-1:
    #                 for codeDate in jsonList:
    #                     if str(acValue) == codeDate['key_id']:
    #                         code = codeDate['pulse']
    #                         codeList = code.split(",")
    #             else:
    #                 for codeDate in jsonList:
    #                     if str(acValue) == codeDate['par']:
    #                         code = codeDate['pulse']
    #                         codeList = code.split(",")
    #
    #     # 关闭Cursor:
    #     cursor.close()
    #     # 提交事务:
    #     conn.commit()
    #     # 关闭Connection:
    #     conn.close()
    #
    #     return codeList,kfid




    def ac_control(self, device_id, acValue):
        print("ac_control acValue:",acValue)
        sendResponse=-1
        device={}
        code,kfid=self.get_code(device_id,acValue)
        print("kfidkfidkfidkfid:",kfid)
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
                print("先假定收到了码库为:'354,1046,354' ")
                #先假定收到了码库为:'354,1046,354'
                #code=get_servers_ac_code(code,kfid)
                code='354,1046,354'

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


