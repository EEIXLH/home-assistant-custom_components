import sqlite3
db_path="irdevices.db"

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

def selectCodeByEndpointId(cursor,endpointId):

    # devId=str(endpointId)
    # print("selectCodeByEndpointId devId:",devId)
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


def modify_device_code(device):
    endpointId = str(device["entity_id"])
    key_id = str(device["key_id"])
    irdata = device["pulse"]
    infraed_str = "infraed_"
    if infraed_str in endpointId:
        num = endpointId.index(infraed_str)
        print("num:", num)
        number = num + 8
        device_id = endpointId[number:]

    else:
        device_id = endpointId
    print("device_id:", device_id)

    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    # 创建一个Cursor:
    cursor = conn.cursor()
    rows = selectCodeByEndpointId(cursor, device_id)
    modifyList = []
    for row in rows:
        if row is not None:
            if type(row["keylist"]) == str:

                keylist = row["keylist"]
            else:
                keylist = row["keylist"].decode('utf-8')
            jsonList = eval(keylist)
            print("jsonList:", jsonList)
            i = 0
            for codeDate in jsonList:
                if str(key_id) == str(codeDate['key_id']):
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

    print("modifyList:", modifyList)
    updateCodeListByEndpointId(cursor, str(modifyList).encode('utf-8'), device_id)

    cursor.close()
    # 提交事务:
    conn.commit()
    # 关闭Connection:
    conn.close()

    # self.discover_devices()
    return

if __name__ == '__main__':
    device={}
    device["entity_id"] ="infraed_11"
    device["key_id"] = 1
    device["pulse"]  = "111,111"
    modify_device_code(device)
    # print(__name__)