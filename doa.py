import os
from tuning import Tuning
import usb.core
import usb.util
import signal
import sys
import time
import datetime
from pathlib import Path

location=sys.argv[1]

directoryPath = os.path.join("recordings", location)
filePath= os.path.join(directoryPath, "doa.csv")
stopPath= os.path.join(directoryPath, "stop.signal")
print(stopPath)

record = open(filePath,'w')
stopPath = Path(stopPath)
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
Mic_tuning=Tuning(dev)
while True:
    t = datetime.datetime.now()
    if Mic_tuning.is_voice():
       doa = Mic_tuning.direction
    else:
       doa =-1
    record.write(str(t)+","+str(doa)+"\n")
    time.sleep(0.05)
    if stopPath.is_file():
       record.close()
       print("Closing DOA file")
       break
