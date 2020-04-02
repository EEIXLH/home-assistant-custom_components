
class MqttException(Exception):
    OK = 0
    ERROR_UNKNOWN = 1
    # 参数校验失败
    ERROR_INVALID_PARAM = 2
    # json格式错误
    ERROR_INVALID_JSON = 3
    # 数据格式正确
    ERROR_INVALID_DATA_FORMAT = 4
    # 创建流失败
    ERROR_INVALID_FLOW = 5
    # 数据未找到
    ERROR_NOT_FOUND = 6
    # 设备忙
    ERROR_DISCONNECTED = 7
    # 组件没有加载
    ERROR_COMPONENT_NOT_LOADED = 8
    # 组件已经加载
    ERROR_COMPONENT_LOADED = 9
    # 没有该组件
    ERROR_INTEGRATION_NOT_FOUND = 10

    def __init__(self, code: int, cause: str):
        Exception.__init__(self, cause)
        self.code = code
