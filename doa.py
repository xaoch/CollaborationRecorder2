import os
from tuning import Tuning
import usb.core
import usb.util
import signal
import sys
import time

def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
    sys.exit(0)

location=sys.argv[1]

signal.signal(signal.SIGTERM, sigterm_handler)

directoryPath = os.path.join("recordings", location)
filePath= os.path.join(directoryPath, "doa.csv")

record = open(filePath,'w')
try:
    dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
    Mic_tuning=Tuning(dev)
    while True:
        t = time.localtime()
        if Mic_tuning.is_voice():
            doa = Mic_tuning.direction
        else:
            doa =-1
        record.write(str(time)+","+str(doa))
        with open('doatemp.txt', 'w') as f:
            f.write(str(time)+","+str(doa))
        os.replace('doatemp.txt','doa.txt')
        time.sleep(0.05)
finally:
    record.close()
    print("Goodbye")