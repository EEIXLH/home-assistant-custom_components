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

        # SESSION.bizType = bizType

        # self.get_access_token()
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



    def get_IR_device(self,deviceId):
        headers = {
            'Authorization': 'Bearer ' + SESSION.accessToken,
            'Content-Type': 'application/json',
        }
        url = "https://api11.ifuturehome.com.cn/pro/v1/devices/"+deviceId+"/subdevices"
        s = requests.session()
        s.keep_alive = False
        logger_obj.debug("get IR device url, url is：  %s" + str(url))
        logger_obj.debug("get IR device headers, headers is：  %s" + str(headers))
        requests.packages.urllib3.disable_warnings()
        body = []
        code=""
        try:
            response = requests.request("GET", url, verify=False, headers=headers,timeout=6)

            code = int(response.status_code)
            logger_obj.debug("get IR device code, code is：  %s"+ str(code))
            if code == 200 or code == 201:
                logger_obj.debug("get IR device success, code is：  %s"+ str(response.status_code))
                jsonBody = json.loads(response.text)
                body=jsonBody["body"]
            else:
                logger_obj.warning("get IR device error, error code is" + str(response.status_code))
                pass
        except Exception as err:
            logger_obj.warning("get IR device error ,Unexpected error : "+ str( err))
            pass

        return body, code


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

        infraed_str = "infraed#"
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
        infraed_str="infraed#"
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


    def ir_control(self, endpointId, propertyName, value, param=None):

        codeType={
            'format': 1,
            'fre': 37900,
            'irdata_id': 11272,
            'keys': [
                {
                    'dcode': None,
                    'exts': None,
                    'fid': 0,
                    'fkey': 'power_off',
                    'fname': '',
                    'format': 0,
                    'scode': None,
                    'pulse': value["pulse"]
                }
            ],
            'rid': 1,
            'type': 2
        }

        jsonBody = json.dumps(codeType)  # 转成 JSON字符串
        value = jsonBody.encode()  # 编码
        value = gzip.compress(value)  # 压缩
        datapointValue = value.hex()  #转16进制
        if param is None:
            param = {}
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging control ir device time is"+str(nowTime))
        response, code = self.control_request(endpointId, propertyName, datapointValue, param)
        if code == 200 or code == 201:
            logger_obj.debug("ir control success, code is：  %s"+ str(code))
            nowTime = datetime.datetime.now()
            logger_obj.debug("finish control ir device time is：  %s"+str(nowTime))
            success = True
        else:
            logger_obj.warning("ir control fail, code is：  %s"+ str(code))
            nowTime = datetime.datetime.now()
            logger_obj.warning("finish control ir device time is：  %s"+str(nowTime))
            success = False
        return success, response


    def retrieves_properties(self,deviceId):
        headers = {
            'Authorization': 'Bearer ' + SESSION.accessToken,
            'Content-Type': 'application/json',
        }
        url = "https://" + AYLA_DEVICE_SERVER + ":443/apiv1/dsns/"+deviceId+"/properties.json"
        requests.packages.urllib3.disable_warnings()
        nowTime = datetime.datetime.now()
        logger_obj.debug("beging retrieves_properties time is" + str(nowTime))
        propertyData = []
        try:
            response = requests.request("GET", url, verify=False, headers=headers,timeout=6)

            code = int(response.status_code)
            if code==200 or code==201:
                logger_obj.debug("retrieves_properties success, code is：  %s" + str(response.status_code))
                nowTime = datetime.datetime.now()
                logger_obj.debug("finish retrieves_properties device time is：  %s" + str(nowTime))
                jsonBody = json.loads(response.text)
                for property in jsonBody:
                    dict = {}
                    property = property["property"]
                    if property["value"] != None:
                        if property["name"] == "switch1":
                            if int(property["value"]) == 0:
                                dict["state"]=False
                            else:
                                dict["state"] =True
                            propertyData.append(dict)

                        elif property["name"] == "switch":
                            if int(property["value"]) == 0:
                                dict["state"]=False
                            else:
                                dict["state"] =True
                            propertyData.append(dict)

                        elif property["name"] == "brightness":
                            dict["brightness"] = int(property["value"]* 255 / 100)
                            propertyData.append(dict)

                        elif property["name"] == "CCT":
                                dict["color_temp"] = int(property["value"])
                                propertyData.append(dict)

                        elif property["name"] == "workmode":
                            dict["workmode"] = int(property["value"])
                            propertyData.append(dict)

                        elif property["name"] == "humi":
                            dict["target_humidity"] = int(property["value"])
                            propertyData.append(dict)

                        elif property["name"] == "realhumi":
                            dict["current_humidity"] = int(property["value"])
                            propertyData.append(dict)
                        elif property["name"] == "mist":
                            dict["mist"] = int(property["value"])
                            propertyData.append(dict)
                        else:
                            pass
                    else:
                        pass
            else:
                logger_obj.warning("retrieves device properties error, error code is：  %s" +str(response.status_code))
                nowTime = datetime.datetime.now()
                logger_obj.warning("finish retrieves_properties device time is：  %s"+ str(nowTime))
        except Exception as err:
            logger_obj.warning("retrieves device properties error ,Unexpected error : "+ str( err))
            pass
        return  propertyData


    def get_single_device(self,deviceId):
        headers = {
            'Authorization': 'Bearer ' + SESSION.accessToken,
            'Content-Type': 'application/json',
        }
        url = "https://" + AYLA_DEVICE_SERVER + ":443/apiv1/dsns/"+deviceId+".json"
        requests.packages.urllib3.disable_warnings()
        product_name = None
        connection_status=True
        try:
            response = requests.request("GET", url, verify=False, headers=headers,timeout=6)
            code = int(response.status_code)
            if code==200 or code==201:
                logger_obj.debug("get_single_device success, code is" + str(response.status_code))
                jsonBody = json.loads(response.text)
                product_name=jsonBody["device"]["product_name"]
                connection_status=jsonBody["device"]["connection_status"]
            else:
                logger_obj.warning("get_single_device error, error code is " +str(response.status_code))
                pass
        except Exception as err:
            logger_obj.warning("get_single_device error,Unexpected error : "+ str( err))
            pass
        # print("product_name,connection_status:",product_name,connection_status)
        return  product_name,connection_status


    def get_alldevice(self):

        headers = {
            'Authorization': 'Bearer ' + SESSION.accessToken,
            'Content-Type': 'application/json',
        }
        url = "https://" + AYLA_DEVICE_SERVER + ":443/apiv1/devices.json"
        requests.packages.urllib3.disable_warnings()
        jsonBody=[]
        code=""
        try:
            response = requests.request("GET", url, verify=False, headers=headers,timeout=6)

            jsonBody = []
            code = int(response.status_code)
            if code == 200 or code == 201:
                logger_obj.debug("get all device success, code is ：  %s" + str(response.status_code))
                jsonBody = json.loads(response.text)
            else:
                logger_obj.warning("get all device fail, code is ：  %s" + str(response.status_code))
                pass
        except Exception as err:
            logger_obj.warning("get all device  error,Unexpected error : "+ str( err))

            response = requests.request("GET", url, verify=False, headers=headers, timeout=6)

            jsonBody = []
            code = int(response.status_code)
            if code == 200 or code == 201:
                logger_obj.debug("retry get all device success, code is ：  %s" + str(response.status_code))
                jsonBody = json.loads(response.text)
            else:
                logger_obj.warning("retry get all device fail, code is ：  %s" + str(response.status_code))
                pass

            pass

        return jsonBody, code

    def getACStateInfo(self, deviceId, subdeviceName):
        headers = {
            'Authorization': 'auth_token ' + SESSION.accessToken,
            'Content-Type': 'application/json',
        }
        url = "https://api11.ifuturehome.com.cn/pro/v1/smartvoice/get_ac_state?device_id=" + deviceId + "&subdevice_name=" + subdeviceName
        requests.packages.urllib3.disable_warnings()
        code=""
        dict = {}
        try:
            response = requests.request("GET", url, verify=False, headers=headers,timeout=6)
            body = []
            code = int(response.status_code)

            if code == 200 or code == 201:
                logger_obj.debug("get AC State Info success, code is ：  %s" + str(response.status_code))
                jsonBody = json.loads(response.text)
                jsonBody = jsonBody["body"]
                dict["state"] = jsonBody["curPowerState"]
                dict["mode_list"] = jsonBody["mode_list"]
            else:
                logger_obj.warning("get AC State Info error, error code is：  %s" + str(response.status_code))
                pass
        except Exception as err:
            logger_obj.warning("get AC State Info  error,Unexpected error : "+ str( err))
            pass

        return dict, code


    def getIrCode(self,irdata_id):
        irdatas=""
        headers = {
            'Authorization': 'auth_token ' + SESSION.accessToken,
            'Content-Type': 'application/json',
        }
        url = "https://api11.ifuturehome.com.cn/pro/v1/irdatas/" + str(irdata_id)
        requests.packages.urllib3.disable_warnings()
        logger_obj.debug("get IR code url, url is：  %s" + str(url))
        logger_obj.debug("get IR code headers, headers is：  %s" + str(headers))
        code=""
        try:
            response = requests.request("GET", url, verify=False, headers=headers,timeout=10)
            code = int(response.status_code)
            if code == 200 or code == 201:
                logger_obj.debug("get Ir code success, code is ：  %s" + str(response.status_code))
                jsonBody = json.loads(response.text)
                irdatas = jsonBody["body"]
            else:
                logger_obj.warning("get Ir code  error, error code is：  %s" + str(response.status_code))
                pass
        except Exception as err:
            logger_obj.warning("get Ir code  error, Unexpected error : "+ str( err))
            pass
        return irdatas,code



    def changeChannel(self,type, subdeviceName, channelValue, endpointId, propertyName):
        headers = {
            'Authorization': 'auth_token ' + SESSION.accessToken,
            'Content-Type': 'application/json',
        }
        if type=="name":
            url = "https://api11.ifuturehome.com.cn/pro/v1/smartvoice/irdata_by_channel_number?device_id=" + endpointId + "&subdevice_name=" + subdeviceName + "&channel_name=" + channelValue

        elif type=="number":
            url = "https://api11.ifuturehome.com.cn/pro/v1/smartvoice/irdata_by_channel_number?device_id=" + endpointId + "&subdevice_name=" + subdeviceName + "&channel_number=" + str(channelValue)
        logger_obj.debug("control AC Device url, url is：  %s" + str(url))
        requests.packages.urllib3.disable_warnings()
        dict = {}
        code=""
        try:
            response = requests.request("GET", url, verify=False, headers=headers,timeout=6)
            body = []
            code = int(response.status_code)

            if code == 200 or code == 201:
                jsonBody = json.loads(response.text)  # 将已编码的 JSON 字符串解码为 Python 对象
                if int(jsonBody["statusCode"]) != 200 or int(jsonBody["statusCode"]) != 201:  # 提取body
                    logger_obj.warning("get change Channel  fail, jsonBody is " + str(jsonBody))
                    pass
                else:
                    jsonBody = jsonBody["body"]  # 提取body
                    jsonBody = json.dumps(jsonBody)  # 转成 JSON字符串
                    value = jsonBody.encode()  # 编码
                    value = gzip.compress(value)  # 压缩

                    datapointValue = value.hex()
                    param = {}
                    response, code = self.control_request(endpointId, propertyName, datapointValue, param)
                    if code == 200 or code == 201:
                        logger_obj.debug("change Channel success, code is：  %s" + str(code))
                        pass
                    else:
                        logger_obj.warning("change Channel fail, code is ：  %s" + str(code))
                        pass
            else:
                pass
        except Exception as err:
            logger_obj.warning("change Channel erro, Unexpected error : " + str(err))
            pass

        return dict, code


    def controlACDevice(self, irEndpointId, subdeviceName, keyID, endpointId, propertyName):

        headers = {
            'Authorization': 'auth_token ' + SESSION.accessToken,
            'Content-Type': 'application/json',
        }
        url = "https://api11.ifuturehome.com.cn/pro/v1/smartvoice/control_ac?device_id=" + endpointId + "&subdevice_name=" + subdeviceName + "&ac_param=" + keyID

        requests.packages.urllib3.disable_warnings()
        dict = {}
        code=""
        try:
            response = requests.request("GET", url, verify=False, headers=headers,timeout=6)
            body = []
            code = int(response.status_code)

            if code == 200 or code == 201:
                jsonBody = json.loads(response.text)    #将已编码的 JSON 字符串解码为 Python 对象
                logger_obj.debug("control AC Device statusCode, statusCode is：  %s" + str(jsonBody["statusCode"]))
                if int(jsonBody["statusCode"]) == 200 or int(jsonBody["statusCode"]) == 201:  # 提取body
                    logger_obj.debug("get control AC Device success, jsonBody is ：  %s" + str(jsonBody))
                    jsonBody = jsonBody["body"]  # 提取body
                    jsonBody = json.dumps(jsonBody)  # 转成 JSON字符串
                    value = jsonBody.encode()  # 编码
                    value = gzip.compress(value)  # 压缩

                    datapointValue = value.hex()
                    param = {}
                    response, code = self.control_request(endpointId, propertyName, datapointValue, param)
                    if code == 200 or code == 201:
                        logger_obj.debug("control AC Device success, code is ：  %s" + str(code))
                        pass
                    else:
                        logger_obj.warning("control AC Device fail, code is ：  %s" + str(code))

                        pass
                else:

                    logger_obj.warning("get control AC Device fail, jsonBody is ：  %s"+ str(jsonBody))
                    pass
            else:
                pass
        except Exception as err:
            logger_obj.warning("get control AC Device fail, Unexpected error : "+ str(err))
            pass
        return dict, code


    def controlIRDevice(self, irEndpointId, subdeviceName, keyID, endpointId, propertyName):
        headers = {
            'Authorization': 'auth_token ' + SESSION.accessToken,
            'Content-Type': 'application/json',
        }
        url = "https://api11.ifuturehome.com.cn/pro/v1/smartvoice/irdata_by_fid?device_id=" + endpointId + "&subdevice_name=" + subdeviceName + "&fid=" + keyID
        requests.packages.urllib3.disable_warnings()
        dict = {}
        code=""
        try:
            response = requests.request("GET", url, verify=False, headers=headers,timeout=6)
            body = []
            code = int(response.status_code)

            if code == 200 or code == 201:
                jsonBody = json.loads(response.text)    #将已编码的 JSON 字符串解码为 Python 对象

                if int(jsonBody["statusCode"])!=200 and int(jsonBody["statusCode"]) != 201: #提取body
                    logger_obj.warning("control IR Device fail, jsonBody is " + str(jsonBody))

                    pass
                else:
                    jsonBody = jsonBody["body"]  # 提取body
                    jsonBody=json.dumps(jsonBody) #转成 JSON字符串
                    value = jsonBody.encode()  #编码
                    value = gzip.compress(value)   #压缩
                    datapointValue = value.hex()
                    param = {}
                    response, code = self.control_request(endpointId, propertyName, datapointValue, param)
                    if code == 200 or code == 201:
                        logger_obj.debug("control IR Device success, code is ：  %s" +str(code))
                        pass
                    else:
                        logger_obj.warning("control IR Device fail, code is ：  %s" +str(code))
                        pass
            else:
                pass
        except Exception as err:
            logger_obj.warning("control IR Device fail, Unexpected error : "+ str(err))
            pass
        return dict, code


    def controlIRDeviceExceptAC(self, irEndpointId, subdeviceName, keyID, endpointId, propertyName):
        headers = {
            'Authorization': 'auth_token ' + SESSION.accessToken,
            'Content-Type': 'application/json',
        }
        url="https://api11.ifuturehome.com.cn/pro/v1/smartvoice/irdata_by_fid?device_id=" + endpointId + "subdevice_name=" + subdeviceName + "fid=" + keyID
        requests.packages.urllib3.disable_warnings()
        dict = {}
        code=""
        try:
            response = requests.request("GET", url, verify=False, headers=headers,timeout=6)
            body = []
            code = int(response.status_code)

            if code == 200 or code == 201:
                jsonBody = json.loads(response.text)    #将已编码的 JSON 字符串解码为 Python 对象
                if int(jsonBody["statusCode"]) != 200 or int(jsonBody["statusCode"]) != 201:  # 提取body
                    logger_obj.warning("control IR Device Except AC fail, jsonBody is " + str(jsonBody))
                    pass
                else:
                    logger_obj.info("control IR Device Except AC success, jsonBody is " + str(jsonBody))
                    jsonBody = jsonBody["body"] #提取body
                    jsonBody=json.dumps(jsonBody) #转成 JSON字符串
                    value = jsonBody.encode()  #编码
                    value = gzip.compress(value)   #压缩
                    datapointValue = value.hex()
                    param = {}
                    response, code = self.control_request(endpointId, propertyName, datapointValue, param)
                    if code == 200 or code == 201:

                        logger_obj.debug("control IR Device Except AC success, code is ：  %s" +str(code))
                        pass
                    else:
                        logger_obj.warning("control IR Device Except AC fail, code is：  %s"+ str(code))
                        pass
            else:
                pass
        except Exception as err:
            logger_obj.warning("control IR Device Except AC fail, Unexpected error : "+ str(err))
            pass

        return dict, code



class iFutureHomeAPIException(Exception):
    pass


