import os, sys, stat
from shutil import copyfile
#from py_irsend import irsend


filesPath='demo.lircd.conf' 
copyCMD=""
newCode_file_name='newCode.txt'

def get_light_code():
   

    cir_data=[0xd,0x4,0xd,0x3,0x4,0xc,0xd,0x4,0xd,0x4,0xd,0x4,0xd,0x3,0x4,0xc,0x4,0xc,0x4,0xc,0x4,0xc,0x4,0x4c,0xd,0x3,0xd,0x4,0x4, 
        0xc,0xd,0x3,0xd,0x3,0xd,0x4,0xd,0x4,0x4,0xc,0x4,0xc,0x4,0xc,0x4,0xc,0x4,0x4c,0xd,0x3,0xd,0x3,0x4,0xc,0xd,0x4,0xd,0x4, 
        0xd,0x3,0xd,0x4,0x4,0xc,0x4,0xc,0x4,0xc,0x4,0xc,0x4,0x4c,0xd,0x4,0xd,0x4,0x4,0xc,0xd,0x3,0xd,0x3,0xd,0x4,0xd,0x3,0x4, 
        0xc,0x4,0xc,0x4,0xc,0x4,0xc,0x4,0x4c,0xd,0x3,0xd,0x3,0x4,0xc,0xd,0x4,0xd,0x3,0xd,0x3,0xd,0x4,0x4,0xc,0x4,0xc,0x4,0xc, 
        0x4,0xc,0x4,0x4c,0xd,0x4,0xd,0x3,0x4,0xc,0xd,0x4,0xd,0x4,0xd,0x3,0xd,0x3,0x4,0xc,0x4,0xc,0x4,0xc,0x4,0xc,0x4]
    lightCodeList=[]
    for code  in cir_data:
        if int(code)==0:
            pass 
        else:
            timeCode=code*100
            lightCodeList.append(timeCode)
    print("lightCodeList =",lightCodeList)
    return lightCodeList


def read_learn_file(newCode_file_name):
    with open(newCode_file_name) as f:
        content = f.read()
        line = content.strip('\n')
        line2=line[:-1]
        codeList=line2.split(",") 
    print("learn code List =",codeList)
    return codeList

def write_code_config(remoteName,buttonNameKey,codeList):
    f = open(filesPath,'w') 
    f.write('begin remote' + '\n'+ '\n'+'  name  '+ remoteName+'\n'+'  flags RAW_CODES'+ '\n'+'  eps            30'+ '\n'+'  aeps          100'+ '\n'+ '\n') 
    f.write('  gap          19991' + '\n'+ '\n'+'      begin raw_codes' + '\n'+ '\n') 
    f.write('          name ' +buttonNameKey+'\n') 
    timeCode="" 
    i=0
    for code  in codeList:
        i=i+1
        if "-"in str(code) :
            pass
            # str2 = "-"
            # num=code.index(str2)
            # endCode=code[:code.index(str2)]
            # print("endCode =",endCode)
        else:
            endCode =code
        if i<5:
            pass
        else:
            i=1
            f.write('\n') 
        f.write('      '+str(endCode)) 
    
    f.write('\n'+ '\n'+"      end raw_codes"+'\n'+ '\n'+"end remote") 
    f.close()
    os.system('sudo cp  demo.lircd.conf  /etc/lirc/lircd.conf.d')
    return 

def send_code(codeList):
    print("--------------beging send_code function-------------- ")
    remoteName='demo'
    buttonNameKey="on" 
    write_code_config(remoteName,buttonNameKey,codeList)
    os.system('sudo service lircd restart')
    os.system('irsend SEND_ONCE demo on')

    # name='demo'
    # nameKey="on"
    #irsend.send_once(remoteName,[buttonNameKey])
    return "send succeed"

    
if __name__ == '__main__':

    #codeList=read_learn_file(newCode_file_name)
    codeList=get_light_code()
    #response=send_code(codeList)

    #print("send Code result :",response)
