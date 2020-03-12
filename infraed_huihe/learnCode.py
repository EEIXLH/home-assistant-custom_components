import sys,os,subprocess,time
file_name = 'learnCode.txt'
newCode_file_name='newCode.txt'


#读取日志，寻找第一个完整的红外码，并返回红外码
def read_code_file():
    list_slice=[]
   
    space_str="space"
    code=""
    getCode=""
    with open(file_name) as f:
        content = f.read()
        code=content.rstrip()
        getCode=','.join(code.split())
        # print(getCode)

    list3 = getCode.split(",")

    i=0
    space1=0
    j=0
    for key in list3:
        i=i+1
        if "space"in key:
            j=j+1
            if j>=2:
                print("enddddddd1-space1=",i-space1)
                if i-space1>30:
                    os.system('pkill mode2')
                    list_slice = list3[space1:i:1]
                    break
                else:
                    pass
            else:
                pass
            space1=i
        else:
            pass
    print("space1=",space1)
    print("i=",i)
    print("enddddddd1-space1=",i-space1)
   
    return list_slice

#将获取的红外码存入newCode.txt
def write_learn_code(learn_code):
    print("*********** coming write_learn_code ***********")
    file_write_obj = open(newCode_file_name, 'w')
    i=0
    for code in learn_code:
        if "-"in str(code) :
           pass
        else:
            value =code
            file_write_obj.write(value+",")
    file_write_obj.write('\n')

    print("finish write_learn_code ")
    return

#读取newCode.txt的红外码
def read_learn_file(newCode_file_name):
    with open(newCode_file_name) as f:
        content = f.read()
        line = content.strip('\n')
        codeList=line.split(",") 
        print("learn code List =",codeList)
        # c=list(content)
        # print("read_learn_file =",content)

def stop_learn():
    os.system('pkill mode2')

def learn_code():
    print("*********** coming learn code ***********")
    learn_code=[]
    getList=[]
    a=subprocess.Popen("mode2 -m -d /dev/lirc1 >"+ file_name, shell=True)
    waitTime=0
    while waitTime<60:
        print("waitTime:",waitTime)
        time.sleep(1)
        getList=read_code_file()
        print("getList:",getList)
        if getList!=[]:
            learn_code=getList
            waitTime=60
        else:
            waitTime=waitTime+1
    else:
        pass

        
    write_learn_code(learn_code)
    # read_learn_file(newCode_file_name)
    print("finish learn_code ：",learn_code)
    
    return learn_code
        

    
if __name__ == '__main__':

    Code=learn_code()
    print("get learn Code:",Code)


