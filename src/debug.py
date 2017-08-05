import os
import os.path

DEBUG = False

if DEBUG:
    log_dir = os.path.join('..', 'logs')

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    old_logs = os.listdir(log_dir)

    index = 0
    logfilename = None
    while True:
        logfilename = os.path.join(log_dir, 'log{:04d}'.format(index))
        if os.path.exists(logfilename):
            index += 1
            continue
        else:
            break

    logfilehandle = None

    def db(text):
        global logfilehandle
        if logfilehandle is None:
            logfilehandle = open(logfilename, 'w')
        logfilehandle.write(str(text))
        logfilehandle.write('\n')
        logfilehandle.flush()

else:
    def db(*args, **kwargs):
        pass
