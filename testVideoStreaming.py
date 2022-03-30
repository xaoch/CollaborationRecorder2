import ffmpeg
import socket
import os
import threading
import time
import signal

stop_doa=False


def getDoa():
    while True:
        os.system("sudo python doa.py")
        time.sleep(0.05)
        global stop_doa
        if stop_doa:
            break

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname+".local" )
print ("IP",IPAddr)
i=0

#x = threading.Thread(target=getDoa)
#x.start()

#audio = ffmpeg.input("default",f="alsa",channels=1,sample_rate=44100)
audio = ffmpeg.input("sysdefault",  **{'async': 1},f="alsa", channels=1, sample_rate=44100)
video = ffmpeg.input("/dev/video0", f="v4l2", input_format="h264", video_size=(1080, 1080))
#video = ffmpeg.input("/dev/video0",f="v4l2",input_format="h264",video_size=(1280, 976),framerate=15)
#text = video.drawtext(textfile="doa.txt",reload=1,fontcolor="red",x=40,y=40,fontsize="64",escape_text=True)
#out1 = ffmpeg.output(audio,video,"rtmp://localhost:1935/live/1",f="flv", vcodec="copy")
#out2 = ffmpeg.output(audio,video, "output.mp4", vsync=1, async=1, vcodec="copy")
#out3 = ffmpeg.output(text, "outputText.mp4",preset="ultrafast")
#out=ffmpeg.merge_outputs(out1,out2,out3)
out = ffmpeg.output(audio, video, "recordings/output.mp4", vcodec="copy")
print(ffmpeg.get_args(out))
proc=ffmpeg.run_async(out)
time.sleep(5)
proc.send_signal(signal.SIGINT)
proc.wait()
print("Stoping")
#stop_doa=True
#x.join()
