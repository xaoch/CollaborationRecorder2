import ffmpeg
import socket
from tuning import Tuning
import usb.core
import usb.util
import os
import threading
import time

strop_doa=False


def getDoa():
    while True:
        global Mic_tuning
        if Mic_tuning.is_voice():
            doa = Mic_tuning.direction
        else:
            doa =-1
        print(doa)
        with open('doatemp.txt', 'w') as f:
            f.write(str(doa))
        os.replace('doatemp.txt','doa.txt')
        time.sleep(0.05)
        global stop_doa
        if stop_doa:
            break

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname+".local" )
print ("IP",IPAddr)
i=0
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
Mic_tuning=Tuning(dev)
x = threading.Thread(target=getDoa)
x.start()



audio = ffmpeg.input("default",f="alsa",channels=1,sample_rate=44100)
video = ffmpeg.input("/dev/video0",f="v4l2",input_format="h264",video_size=(1280, 976),framerate=15)
text = video.drawtext(textfile="doa.txt",reload=1,fontcolor="red",x=40,y=40,fontsize="64",escape_text=True)
out1 = ffmpeg.output(audio,video,"rtmp://localhost:1935/live/1",f="flv", vcodec="copy")
out2 = ffmpeg.output(audio,video, "output.mp4", vcodec="copy")
out3 = ffmpeg.output(text, "outputText.mp4",preset="ultrafast")
out=ffmpeg.merge_outputs(out1,out2,out3)
print(ffmpeg.get_args(out))
#ffmpeg.run(out)
stop_doa=True
x.join()
