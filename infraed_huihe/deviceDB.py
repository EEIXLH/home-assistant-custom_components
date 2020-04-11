from .log import logger_obj

def createTable(cursor):
    cursor.execute(
        'create table  if  not  exists  device (deviceiId INTEGER PRIMARY KEY , deviceName varchar(20) ,devicetType varchar(20)'
        ',kfid varchar(20),keylist varchar(64));')






def insertOneDevice(cursor,device):

    deviceName = device["device_name"]
    devicetType = device["device_type"]
    kfid = device["kfid"]
    keylist = device["keylist"]
    list = str(keylist)
    cursor.execute("insert into device(deviceName, devicetType, kfid,keylist) values (?,?,?,?)",
                   (deviceName, devicetType, kfid, list.encode('utf-8')))
    # 通过rowcount获得插入的行数:
    num = cursor.rowcount
    if num == 1:
        return True

    else:
        return False



def insert(conn,deviceName, devicetType, kfid, keylist):
    """
    插入一行的数据
    """
    sql_insert = '''
        INSERT INTO
          device(deviceName, devicetType,kfid,keylist)
        VALUES
          (?, ?, ?, ?);
        '''

    D=conn.execute(sql_insert, (deviceName, devicetType, kfid, keylist))

    logger_obj.info("插入数据成功：  %s",D)



def selectAll(cursor):

    cursor.execute('select * from device')
    rows = cursor.fetchall()


    device_list = []
    for row in rows:
            d = {}
            d['device_id'] = row[0]
            d['device_name'] = row[1]
            d['device_type'] = row[2]
            d['kfid'] = row[3]
            if type(row[4])== str:
                d['keylist'] = row[4]
            else:
                d['keylist'] = row[4].decode('utf-8')
            device_list.append(d)
    return device_list


def selectCodeByEndpointId(cursor,endpointId):

    # devId=str(endpointId)
    # sql =  '''
    # SELECT * FROM device WHERE deviceiId= ?
    # '''
    # cursor.execute(sql,devId)
    # rows = cursor.fetchall()

    devId = str(endpointId)
    rows = []
    cursor.execute('select * from device')
    device_list = cursor.fetchall()
    for device in device_list:
        d = {}
        d['device_id'] = device[0]
        d['device_name'] = device[1]
        d['device_type'] = device[2]
        d['kfid'] = device[3]
        if type(device[4]) == str:
            d['keylist'] = device[4]
        else:
            d['keylist'] = device[4].decode('utf-8')
        if str(device[0]) == devId:
            rows.append(d)


    return rows




def deleteOneDevice(cursor,dev_id):
    """
    根据 id 删除对应的那条数据
    """

    sql_delte = '''
    DELETE FROM
      device
    WHERE
      deviceiId=?
    '''
    # tuple 只有一个元素的时候必须是这种写法
    cursor.execute(sql_delte, dev_id)
    logger_obj.info("删除设备  %s  成功 ", dev_id)

    return


def updateCodeListByEndpointId(conn, keylist, deviceiId):
    """
    更新相应部分的数据
    """
    sql_update = '''
    UPDATE
      `device`
    SET
      `keylist`=?
    WHERE
      `deviceiId`=?
    '''
    conn.execute(sql_update, (keylist, int(deviceiId)))

    return


