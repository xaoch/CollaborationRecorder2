import ffmpeg
import socket


hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname+".local" )
print ("IP",IPAddr)

def time():
    return "Hola"

audio = ffmpeg.input("default",f="alsa",channels=1,sample_rate=44100)
video = ffmpeg.input("/dev/video0",f="v4l2",input_format="h264",video_size=(1024, 976),framerate=15)
#video = video.drawtext(text=f"{time()}",fontsize=64, y=100, x=100,fontcolor='white',escape_text=True)
#video = video.split()
out1 = ffmpeg.output(audio,video,"rtmp://localhost:1935/live/1",f="flv", vcodec="copy")
out2 = ffmpeg.output(audio,video, "output.mp4", vcodec="copy")
out=ffmpeg.merge_outputs(out1,out2)
print(ffmpeg.get_args(out))
ffmpeg.run(out)