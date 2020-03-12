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
        ch.setLevel(logging.INFO)                           #定义屏幕输出流的告警级别；
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

stage="pro"
level=2
logger_obj=get_logger(stage,level)




