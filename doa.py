import os
from tuning import Tuning
import usb.core
import usb.util

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
Mic_tuning=Tuning(dev)
if Mic_tuning.is_voice():
    doa = Mic_tuning.direction
else:
    doa =-1
print(doa)
with open('doatemp.txt', 'w') as f:
    f.write(str(doa))
os.replace('doatemp.txt','doa.txt')