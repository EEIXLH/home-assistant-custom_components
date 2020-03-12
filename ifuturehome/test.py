import requests
import json
import time

# coding:utf-8
import colorlog  # 控制台日志输入颜色
import logging
log_colors_config = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'purple',
}



def get_logger(stage,level):

    logger_obj = logging.getLogger()
    if level==1:
        logger_obj.setLevel(logging.DEBUG)
    elif level==2:
        logger_obj.setLevel(logging.INFO)
    elif level==3:
        logger_obj.setLevel(logging.WARNING)
    elif level==4:
        logger_obj.setLevel(logging.ERROR)
    else:
        logger_obj.setLevel(logging.CRITICAL)

    if stage=="pro":

        ch = logging.StreamHandler()                           #创建一个屏幕输出流；
        ch.setLevel(logging.ERROR)                           #定义屏幕输出流的告警级别；
        formater = logging.Formatter('%(asctime)s-[%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s')  # 自定义日志的输出格式，这个格式可以被文件输出流和屏幕输出流调用；
        ch.setFormatter(formater)
        logger_obj.addHandler(ch)

    else:

        ch = logging.StreamHandler()  # 创建一个屏幕输出流；
        ch.setLevel(logging.DEBUG)  # 定义屏幕输出流的告警级别；
        formater =colorlog.ColoredFormatter('%(log_color)s[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s',log_colors=log_colors_config)  # 日志输出格式
        ch.setFormatter(formater)
        logger_obj.addHandler(ch)

    return logger_obj                                      #将我们创建好的logger对象返回

stage="dev"
level=1
logger_obj=get_logger(stage,level)





def getIrCode(self, irdata_id):
    irdatas = ""
    headers = {
        'Authorization': 'auth_token 1243443434',
        'Content-Type': 'application/json',
    }
    url = "https://api11.ifuturehome.com.cn/pro/v1/irdatas/" + str(irdata_id)
    requests.packages.urllib3.disable_warnings()
    logger_obj.debug("get IR code url, url is：  %s" + str(url))
    logger_obj.debug("get IR code headers, headers is：  %s" + str(headers))
    code = ""
    try:
        time.sleep(6)
        response = requests.request("GET", url, verify=False, headers=headers, timeout=6)
        code = int(response.status_code)
        if code == 200 or code == 201:
            logger_obj.debug("get Ir code success, code is ：  %s" + str(response.status_code))
            jsonBody = json.loads(response.text)
            irdatas = jsonBody["body"]
        else:
            print(date)
            logger_obj.warning("get Ir code  error, error code is：  %s" + str(response.status_code))
            pass

    except Exception as err:
        logger_obj.warning("get Ir code  error, Unexpected error: "+ str( err))
        pass
    # except Exception as e:
    #     logger_obj.warning("get IR device error, Unexpected error ", sys.exc_info()[0])
    #     pass
    return irdatas, code
irdata_id="sfsff"
getIrCode(irdata_id,"2424")