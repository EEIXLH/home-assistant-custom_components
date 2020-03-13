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
        print("modify_device_code:", device)
        endpointId = device["entity_id"]
        key_id = device["key_id"]
        irdata = device["irdata"]
        infraed_str="infraed_"
        num=endpointId.index(infraed_str)
        print("num:", num)
        number=num+8
        device_id=endpointId[number:]
        print("device_id:",device_id)

        conn = sqlite3.connect(db_path)
        conn.text_factory = str
        # 创建一个Cursor:
        cursor = conn.cursor()
        rows=selectCodeByEndpointId(cursor,device_id)
        print("modify_device_info:",rows)
        modifyList=[]
        for row in rows:
            if row is not None:
                print("row---row:", row)
                if type(row[4]) == str:
                    keylist = row[4]
                else:
                    keylist = row[4].decode('utf-8')
                jsonList = eval(keylist)
                i=0
                for code in jsonList:
                    if str(key_id) in code:
                        i=i+1
                        code[str(key_id)]=irdata
                    modifyList.append(code)


                if i==0:
                    print("no same key id")
                    addcode={}
                    addcode[str(key_id)] = irdata
                    modifyList.append(addcode)
        print("modifyList:", modifyList)
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


    def get_code(self,endpointId,codeNme):
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
                keylist = row[4].decode('utf-8')
                jsonList = eval(keylist)
                for code in jsonList:

                    if codeNme in code:
                        code = code[codeNme]
                        codeList = code.split(",")
                        print(":code", codeList)

        # 关闭Cursor:
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()

        return codeList



    def device_control(self,endpointId, codeNme, param=None):

        code=self.get_code(endpointId,codeNme)
        if code !=[]:
            send_code(code)
        if param is None:
            param = {}
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging control device time is"+str(nowTime))

        return ""



class iFutureHomeAPIException(Exception):
    pass


