import os
from tuning import Tuning
import usb.core
import usb.util
import signal
import sys
import time
import datetime

stopCapturing=False

def sigterm_handler(_signo, _stack_frame):
    global stopCapturing
    print("Signal Arrived")
    # Raises SystemExit(0):
    sys.exit(0)
    stopCapturing=True

location=sys.argv[1]

signal.signal(signal.SIGTERM, sigterm_handler)

directoryPath = os.path.join("recordings", location)
filePath= os.path.join(directoryPath, "doa.csv")

record = open(filePath,'w')
try:
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    Mic_tuning=Tuning(dev)
    while True:
        t = datetime.datetime.now().microsecond
        if Mic_tuning.is_voice():
            doa = Mic_tuning.direction
        else:
            doa =-1
        record.write(str(t)+","+str(doa)+"\n")
        with open('doatemp.txt', 'w') as f:
            f.write(str(t)+","+str(doa)+"\n")
        os.replace('doatemp.txt','doa.txt')
        time.sleep(0.05)
        if stopCapturing:
            record.close()
            break;
finally:
    record.close()
    print("Goodbye")