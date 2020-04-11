import json

class creatDevice():
    """Class that loads hyperparameters from a json file.

        """
    def __init__(self, json_path):
        with open(json_path) as f:
            params = json.load(f)  # 将json格式数据转换为字典
            self.__dict__.update(params)

    def save(self, json_path):
        with open(json_path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)  # indent缩进级别进行漂亮打印

    def update(self, json_path):
        """Loads parameters from json file"""
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    def read(self, json_path):
        with open(json_path, 'r') as load_f:
            load_dict = json.load(load_f)
            return  load_dict


    @property  # Python内置的@property装饰器就是负责把一个方法变成属性调用的
    def dict(self):
        """Gives dict-like access to Params instance by `params.dict['learning_rate']"""
        return self.__dict__

#

