import os, time
from py_irsend import irsend
from .log import logger_obj
filesPath = '.homeassistant/demo.lircd.conf'
copyCMD = ""


def write_code_config(remoteName, buttonNameKey, codeList):
    f = open(filesPath, 'w')
    f.write(
        'begin remote' + '\n' + '\n' + '  name  ' + remoteName + '\n' + '  flags RAW_CODES' + '\n' + '  eps            30' + '\n' + '  aeps          100' + '\n' + '\n')
    f.write('  gap          19991' + '\n' + '\n' + '      begin raw_codes' + '\n' + '\n')
    f.write('          name ' + buttonNameKey + '\n')
    timeCode = ""
    i = 0
    for code in codeList:
        if code=='' or code==None or code=="":
            pass
        elif int(code)>=30000 :
            pass
        else:
            i = i + 1
            if "-" in str(code):
                pass
            else:
                endCode = code
            if i < 5:
                pass
            else:
                i = 1
                f.write('\n')
            f.write('      ' + str(endCode))

    f.write('\n' + '\n' + "      end raw_codes" + '\n' + '\n' + "end remote")
    f.close()
    os.system('sudo cp  .homeassistant/demo.lircd.conf  /etc/lirc/lircd.conf.d')
    return


def send_code(codeList):
    logger_obj.info("send_code codeList ：%s",codeList)
    remoteName = 'demo'
    buttonNameKey = "on"
    sendResponse=0
    write_code_config(remoteName, buttonNameKey, codeList)
    restartResponse = os.system('sudo service lircd restart')
    logger_obj.info("restartResponse  ：%s",restartResponse)
    if restartResponse != 0:
        logger_obj.info("sudo service lircd restart is erro")
        return False
    else:
        time.sleep(0.3)

        try:
            logger_obj.info("irsend SEND_ONCE demo on 1")
            sendResponse=os.system('irsend SEND_ONCE demo on')
            #irsend.send_once(remoteName, [buttonNameKey])

        except:
            try:
                logger_obj.info("irsend SEND_ONCE demo on 2")
                os.system('sudo service lircd restart')
                time.sleep(0.5)
                sendResponse = os.system('irsend SEND_ONCE demo on')
                #irsend.send_once(remoteName, [buttonNameKey])
            except:
                logger_obj.info("send_code is err 2")
                return False


    if sendResponse==0:


        return True
    else:

        return False
