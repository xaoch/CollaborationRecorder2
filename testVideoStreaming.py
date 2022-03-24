import ffmpeg
import socket


hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname+".local" )
print ("IP",IPAddr)
i=0

def time():
    global i
    i=i+1
    print(i)
    return i

audio = ffmpeg.input("default",f="alsa",channels=1,sample_rate=44100)
video = ffmpeg.input("/dev/video0",f="v4l2",input_format="h264",video_size=(1280, 976),framerate=15)
text = video.drawtext(text="%{n}",start_number=0,
            fontcolor="red",x=40,y=100,timecode="00:00:00:00",timecode_rate=25,
            fontsize="64",escape_text=True)
out1 = ffmpeg.output(audio,video,"rtmp://localhost:1935/live/1",f="flv", vcodec="copy")
out2 = ffmpeg.output(audio,video, "output.mp4", vcodec="copy")
out3 = ffmpeg.output(text, "outputText.mp4",preset="ultrafast")
out=ffmpeg.merge_outputs(out1,out2,out3)
print(ffmpeg.get_args(out))
ffmpeg.run(out)