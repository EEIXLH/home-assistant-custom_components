import os, sys, stat, time
from shutil import copyfile
from py_irsend import irsend

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
    os.system('sudo cp  demo.lircd.conf  /etc/lirc/lircd.conf.d')
    return


def send_code(codeList):
    print("coming send_code ")
    print("codeList: ",codeList)
    remoteName = 'demo'
    buttonNameKey = "on"
    sendResponse=0
    write_code_config(remoteName, buttonNameKey, codeList)
    restartResponse = os.system('sudo service lircd restart')
    print("restartResponse:", restartResponse)
    if restartResponse != 0:
        print("sudo service lircd restart is erro")
        return False
    else:
        time.sleep(0.3)

        try:
            # sendResponse=os.system('irsend SEND_ONCE demo on')
            irsend.send_once(remoteName, [buttonNameKey])

        except:
            try:
                os.system('sudo service lircd restart')
                time.sleep(0.5)
                # sendResponse = os.system('irsend SEND_ONCE demo on')
                irsend.send_once(remoteName, [buttonNameKey])
            except:

                print("send_code is erro")
                return False


    if sendResponse==0:


        return True
    else:

        return False
