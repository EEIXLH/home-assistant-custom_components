import psutil
from .log import logger_obj
def judgeprocess(processname):
    pl = psutil.pids()
    for pid in pl:
        try:
            if psutil.Process(pid).name() == processname:
                return True
        except:
            return False
    else:
        logger_obj.info("------------------not found------------------" )
        return False



