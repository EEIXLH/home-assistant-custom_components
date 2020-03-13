import psutil




def judgeprocess(processname):
    pl = psutil.pids()
    for pid in pl:
        try:
            if psutil.Process(pid).name() == processname:
                print("pid:", pid)
                print("name:", psutil.Process(pid).name())
                return True
        except:
            return False
    else:
        print("------------------not found------------------")
        return False



