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

REFRESHTIME = 60 * 60 * 12

from .log import logger_obj


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


class iFutureHomeApi:


    def init(self, username, password, bizType=''):
        SESSION.username = username
        SESSION.password = password
        SESSION.bizType = bizType

        if username is None or password is None:
            return None
        else:
            self.get_access_token()
            self.discover_devices()
            return SESSION.devices


    def get_access_token(self):
        url = "https://" + AYLA_DEVICE_SERVER + "/users/sign_in.json"
        headers = {'Content-Type': "application/json"}
        data = {"user":{"email": SESSION.username,
                     "password" : SESSION.password,
                    "application": { "app_id": APPID,
                                     "app_secret": APPSECRET}}}

        try:
            requests.packages.urllib3.disable_warnings()
            response = requests.request("POST", url, verify=False, data=json.dumps(data), headers=headers,timeout=6)
            jsonBody = json.loads(response.text)
            response_json = response.json()
            SESSION.test=jsonBody

            if response_json.get('responseStatus') == 'error':
                message = response_json.get('errorMsg')
                if message == 'error':
                    raise iFutureHomeAPIException("get access token failed")
                else:
                    raise iFutureHomeAPIException(message)

            SESSION.accessToken = response_json.get('access_token')
            SESSION.refreshToken = response_json.get('refresh_token')
            SESSION.expireTime = int(time.time()) + response_json.get('expires_in')
            # print("SESSION.refreshToken",SESSION.refreshToken)
            # print("SESSION.accessToken",SESSION.accessToken)
        except:
            raise iFutureHomeAPIException("get access token failed")


    def check_access_token(self):
        if SESSION.username == '' or SESSION.password == '':
            raise iFutureHomeAPIException("can not find username or password")
            # return
        if SESSION.accessToken == '' or SESSION.refreshToken == '':
            self.get_access_token()
        elif SESSION.expireTime <= REFRESHTIME + int(time.time()):
            self.refresh_access_token()


    def refresh_access_token(self):
        headers = {
            'Content-Type': "application/json"
        }
        data={"user" : {"refresh_token" : SESSION.refreshToken}}
        url = "https://" + AYLA_DEVICE_SERVER + ":443/users/refresh_token.json"
        try:
            requests.packages.urllib3.disable_warnings()
            response = requests.request("POST", url, verify=False, data=json.dumps(data), headers=headers,timeout=6)
            jsonBody = json.loads(response.text)
            response_json = response.json()
        except:
            raise iFutureHomeAPIException('refresh token failed')

        if response_json.get('responseStatus') == 'error':
            raise iFutureHomeAPIException('refresh token failed')

        SESSION.accessToken = response_json.get('access_token')
        SESSION.refreshToken = response_json.get('refresh_token')
        SESSION.expireTime = int(time.time()) + response_json.get('expires_in')


    def poll_devices_update(self):
        self.check_access_token()
        return self.discover_devices()


    def discover_devices(self):
        body, code = self.get_alldevice()
        if code == 200 or code== 201 and len(body) != 0:
            logger_obj.debug("discover devices-get_alldevice success, code is ：  %s" + str(code))
            SESSION.devices = []
            for device in body:
                SESSION.devices.extend(get_huihe_device(device, self))
            return body
        return None


    def get_IR_device(self,deviceId):
        headers = {
            'Authorization': 'Bearer ' +  str(SESSION.accessToken),
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


    def get_all_devices(self):
        return SESSION.devices


    def get_device_by_id(self, dev_id):
        for device in SESSION.devices:
            if device.object_id() == dev_id:
                return device
        return None


    def device_control(self,endpointId, propertyName,  value, param=None):
        if param is None:
            param = {}
        nowTime = datetime.datetime.now()
        logger_obj.warning("beging control device time is"+str(nowTime))
        response, code = self.control_request(endpointId, propertyName,value, param)
        if code == 200 or code==201:
            logger_obj.warning("device control success, code is" + str(code))
            nowTime = datetime.datetime.now()
            logger_obj.warning("finish control device time is"+str(nowTime))
            success = True
        else:
            logger_obj.warning("device control fail, code is" + str(code))
            nowTime = datetime.datetime.now()
            logger_obj.warning("finish control device time is"+str(nowTime))
            success = False
        return success,response


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
            'Authorization': 'Bearer ' + str(SESSION.accessToken),
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
            'Authorization': 'Bearer ' + str(SESSION.accessToken),
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
            'Authorization': 'Bearer ' +  str(SESSION.accessToken),
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
            'Authorization': 'auth_token ' +  str(SESSION.accessToken),
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
            'Authorization': 'auth_token ' +  str(SESSION.accessToken),
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


    def control_request(self,endpointId, propertyName, value, payload={}):
        payload['accessToken'] =  str(SESSION.accessToken)
        headers = {
            'Authorization': 'Bearer ' +  str(SESSION.accessToken),
            'Content-Type': 'application/json',
        }
        url = "https://" + AYLA_DEVICE_SERVER + ":443/apiv1/dsns/" + endpointId + "/properties/" + propertyName + "/datapoints.json"

        postBody = {'datapoint': {'value': value}}
        data=json.dumps(postBody)
        requests.packages.urllib3.disable_warnings()
        jsonBody = ""
        code=""
        try:
            response = requests.request("POST", url, verify=False, data=data, headers=headers,timeout=6)
            code = int(response.status_code)
            if int(code)!=200 and int(code)!=201:

                logger_obj.warning("control device error, error code is ：  %s" +str(code))
                pass

            else:
                logger_obj.debug("control device success, code is ：  %s" + str(code))
                jsonBody = json.loads(response.text)
        except Exception as err:
            logger_obj.warning("control device error, Unexpected error : "+ str( err))
            pass

        return jsonBody, code


    def changeChannel(self,type, subdeviceName, channelValue, endpointId, propertyName):
        headers = {
            'Authorization': 'auth_token ' +  str(SESSION.accessToken),
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
            'Authorization': 'auth_token ' +  str(SESSION.accessToken),
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
            'Authorization': 'auth_token ' +  str(SESSION.accessToken),
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
            'Authorization': 'auth_token ' +  str(SESSION.accessToken),
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


