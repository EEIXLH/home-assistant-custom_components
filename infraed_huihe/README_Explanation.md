#------------------------------- infraed_huihe 组件安装使用注意事项 --------------------------------

#### 系统运行环境
    1、升级Home Assistant ，版本号为0.105.5及其以上
    2、升级python，版本是3.7及其以上
    3、下载并安装manifest.json中申明的第三方库
    
#### 配置设置
    1、确保.homeassistant/custom_components 文件下有infraed_huihe和mqtt_client最新的组件。
    2、修改.homeassistant/custom_components/mqtt_client/const.py中HA盒子的序列号 ,BOX_SN = '*******'
    
#### 控制使用
    1、需要在支持lircd服务的Linux中运行，才能成功发送和学习红外码（树莓派）
    


#------------------------------- infraed_huihe 组件接口详情 --------------------------------

#### 增加接设备接口
    SERVICE_ADD_NEW_DEVICE= vol.Schema({
        'device_name': str,
        'device_type': str,
        vol.Optional('kfid', default="-1"): str,
        'keylist': list
    })

#### 设置开始学习接口
    SERVICE_STAR_LEARNING_CODE= vol.Schema({
    vol.Optional('timeout', default=20): int
    })


#### 发送学习码库接口
    SERVICE_SEND_LEARNING_CODE= vol.Schema({
        'pulse': str
    })

#### 发送控制设备码库接口
    SERVICE_CONTROLLING_DEVICE=vol.Schema({
        'entity_id': str,
        'key_id': str
    })


#### 修改设备码库接口
    SERVICE_MODIFY_DEVICE_CODE= vol.Schema({
        'entity_id': str,
        'key_id': str,
        'pulse': str
    })

#### 删除设备接口
    SERVICE_DELETE_DEVICE= vol.Schema({
        'entity_id': str
    })

#"dependencies": ["mqtt_client","voluptuous","sqlite3","time","logging","psutil","subprocess","os","datetime","colorlog","irsend","py_irsend"],