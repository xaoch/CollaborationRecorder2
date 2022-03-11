import ffmpeg
import socket

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname+".local" )
print ("IP",IPAddr)

audio = ffmpeg.input("default",f="alsa",channels=1,sample_rate=44100)
video = ffmpeg.input("/dev/video0",f="v4l2",video_size="1280x768",input_format="h264",framerate=15)
out1 = ffmpeg.output(audio,video,"http://"+IPAddr+":8080",listen=1,f="flv",vcodec="copy")
out2 = ffmpeg.output(audio,video, "output.mp4", vcodec="copy")
out=ffmpeg.merge_outputs(out1,out2)
print(ffmpeg.get_args(out))
ffmpeg.run(out)