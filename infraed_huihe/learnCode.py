import sys, os, subprocess, time
from .judgeProcess import judgeprocess

file_name = 'learnCode.txt'
newCode_file_name = 'newCode.txt'
processname = "mode2"


# 读取日志，寻找第一个完整的红外码，并返回红外码
def read_code_file(processname):
    list_slice = []
    if judgeprocess(processname) == False:
        return False
    else:
        pass
    with open(file_name) as f:
        content = f.read()
        code = content.rstrip()
        getCode = ','.join(code.split())
        # print(getCode)

    list3 = getCode.split(",")

    space = 0
    pulse = 0
    i = 0
    num = 0
    for key in list3:
        i = i + 1
        if "space" in key:
            space = list3.index(key)
        if "pulse" in key:
            pulse = list3.index(key)
        if pulse > space:
            print("pulse-space=", pulse - space)
            num = pulse - space
            if pulse - space > 30:
                list_slice = list3[(space + 1):pulse:1]
                break
            else:
                pass
        else:
            pass

    print("space=", space)
    print("i=", i)
    print("enddddddd-pulse-space=", num)

    return list_slice


# #将获取的红外码存入newCode.txt
# def write_learn_code(learn_code):
#     print("*********** coming write_learn_code ***********")
#     file_write_obj = open(newCode_file_name, 'w')
#     i=0
#     for code in learn_code:
#         if "-"in str(code) :
#            pass
#         else:
#             value =code
#             file_write_obj.write(value+",")
#     file_write_obj.write('\n')
#
#     print("finish write_learn_code ")
#     return
#
# #读取newCode.txt的红外码
# def read_learn_file(newCode_file_name):
#     with open(newCode_file_name) as f:
#         content = f.read()
#         line = content.strip('\n')
#         codeList=line.split(",")
#         print("learn code List =",codeList)
#         # c=list(content)
#         # print("read_learn_file =",content)

def stop_learn():
    os.system('pkill mode2')
    return


def learn_code(timeout):
    print("*********** coming learn code ***********")
    learn_code = []
    getList = []
    a = subprocess.Popen("mode2 -m -d /dev/lirc1 >" + file_name, shell=True)

    waitTime = 0
    while waitTime < timeout:
        print("waitTime:", waitTime)
        time.sleep(1)
        getList = read_code_file(processname)
        print("get List====:", getList)
        if getList != []:
            learn_code = getList
            waitTime = timeout
        elif getList == False:
            learn_code = []
            waitTime = timeout
        else:
            waitTime = waitTime + 1
    else:
        print("pkill mode2")
        os.system('pkill mode2')
        pass

    # write_learn_code(learn_code)
    # read_learn_file(newCode_file_name)
    print("finish learn_code ：", learn_code)

    return learn_code


if __name__ == '__main__':
    Code = learn_code()
    print("get learn Code:", Code)


