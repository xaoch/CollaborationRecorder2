#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import socket
import configparser
import os
import ffmpeg
import sys
import uuid
import time
import signal
import subprocess
from pathlib import Path

num2words = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', \
             6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', \
            11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', \
            15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', \
            19: 'Nineteen', 20: 'Twenty', 30: 'Thirty', 40: 'Forty', \
            50: 'Fifty', 60: 'Sixty', 70: 'Seventy', 80: 'Eighty', \
            90: 'Ninety', 0: 'Zero'}

def n2w(n):
        if n<21:
            return num2words[n]
        else:
            return num2words[n-n%10] + num2words[n%10].lower()

config = configparser.ConfigParser()
config.read(sys.argv[1])

ipMqttServer = config["DEFAULT"]["MQTTServerIp"]
portMqttServer = config["DEFAULT"]["MQTTServerPort"]
#sensorName = config["DEFAULT"]["SensorName"]
streaming = False
previewing = False

ffprocess = None
previewProcess = None
running = "Alive"
stopPath=None

print(portMqttServer)
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname + ".local")
while(not("192.168.50" in IPAddr)):
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname + ".local")
sensorNumber = IPAddr[-2:]
sensorNumber=sensorNumber.replace(".","")
sensorName = n2w(int(sensorNumber))
procDoa=None

def update():
    global previewing
    global streaming
    global running
    if (streaming and ffprocess.poll() != None):
        running = "Problem"
    status = "None"
    if previewing:
        status = "Previewing"
    if streaming:
        status = "Recording"
    client.publish("recorder/update", sensorName + "," + IPAddr + "," + status + "," + running)

def start_previewing():
    global previewProcess
    global previewing

    outputString="rtmp://localhost:1935/live/1"
    previewProcess = subprocess.Popen(["ffmpeg", "-thread_queue_size", "1024", "-video_size","1080x1080",
                                 "-input_format", "h264","-i","/dev/video0","-thread_queue_size","1024",
                                 "-f", "alsa","-async","1","-channels","1","-sample_rate","44100","-i","sysdefault",
                                 "-map","0:v","-map","1:a","-acodec","aac","-vcodec", "copy", "-f","flv",outputString])
    previewing=True
    update()

def stop_previewing():
    global previewing
    if previewing:
        global previewProcess
        previewProcess.send_signal(signal.SIGINT)
        previewProcess.wait()
        print("Stoping Preview")
        previewing = False
    else:
        print("Not previewing")
    update()

def start_streaming(recordingId):
    global stopPath
    global ffprocess
    global streaming
    global procDoa
    directoryPath = os.path.join("recordings", recordingId)
    os.mkdir(directoryPath)
    filePath= os.path.join(directoryPath, sensorName+".mp4")
    stopPath = os.path.join(directoryPath, "stop.signal")

    #doaPath=os.path.join(directoryPath, sensorName+"_doa.mp4")
    ##Old Streaming Solution - generally out of sync
    #audio = ffmpeg.input("sysdefault", f="alsa", channels=1, sample_rate=44100)
    #video = ffmpeg.input("/dev/video0", vf="drawtext=fontfile=roboto.ttf:fontsize=36:fontcolor=yellow:text='%{pts\:gmtime\:1575526882\:%A, %d, %B %Y %I\\\:%M\\\:%S %p}'",f="v4l2", input_format="h264", framerate=15)
    #out1 = ffmpeg.output(audio, video, "rtmp://localhost:1935/live/1", f="flv", vcodec="copy")
    #out2 = ffmpeg.output(audio, video, filePath, vcodec="copy")
    #out = ffmpeg.merge_outputs(out1, out2)
    #audio = ffmpeg.input("sysdefault",  **{'async': 1},f="alsa", channels=1, sample_rate=44100)
    #video = ffmpeg.input("/dev/video0", f="v4l2", input_format="h264", video_size=(1080, 1080))
    #text = video.drawtext(textfile="doa.txt", reload=1, fontcolor="red", x=40, y=40, fontsize="64", escape_text=True)
    #out1 = ffmpeg.output(audio, video, "rtmp://localhost:1935/live/1", f="flv", vcodec="copy")
    #out = ffmpeg.output(audio, video, filePath, vcodec="copy")
    #out3 = ffmpeg.output(text, doaPath, )
    #out = ffmpeg.merge_outputs(out1, out2)#print(out)
    #ffprocess = ffmpeg.run_async(out)

    procDoa = subprocess.Popen(['sudo','python', 'doa.py', recordingId])

    outputString=filePath+"|[f=flv]rtmp://localhost:1935/live/1"
    ffprocess = subprocess.Popen(["ffmpeg", "-thread_queue_size", "1024", "-video_size","1080x1080",
                                 "-input_format", "h264","-i","/dev/video0","-thread_queue_size","1024",
                                 "-f", "alsa","-async","1","-channels","1","-sample_rate","44100","-i","sysdefault",
                                 "-f","tee","-map","0:v","-map","1:a","-acodec","aac","-vcodec", "copy", outputString])
    streaming=True
    update()





def stop_streaming():
    global streaming
    if streaming:
        global ffprocess
        global procDoa
        ffprocess.send_signal(signal.SIGINT)
        ffprocess.wait()
        print("Stoping Video")
        print(stopPath)
        f = open(stopPath, "w")
        print("File Open")
        f.write("Stop!")
        f.close()
        print("File Closed")
        print("Stoping DOA")
        #ffprocess.kill()
        print("Stoping")
        streaming = False
    else:
        print("Not streaming")
    update()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("recorder/control")
    client.publish("recorder/heartbeat", sensorName + "," + IPAddr + "," + str(streaming) + "," + running)


def on_message(client, userdata, msg):
    global streaming
    message = msg.payload.decode()
    messagePart = message.split(",")
    if (messagePart[0] in "start"):
        if (not streaming):
            recordingId=messagePart[1]
            start_streaming(recordingId)
        else:
            print("Already streaming")
    elif (messagePart[0] in "stop"):
        if (streaming):
            stop_streaming()
        else:
            print("Not streaming")
    elif (messagePart[0] in "sensor_start"):
        if (messagePart[1] in sensorName):
            if (not streaming):
                recordingId = messagePart[2]
                start_streaming(recordingId)
            else:
                print("Already streaming")
    elif (messagePart[0] in "sensor_stop"):
        if (messagePart[1] in sensorName):
            if (streaming):
                stop_streaming()
            else:
                print("Not Streaming")
    elif (messagePart[0] in "report_alive"):
        if (streaming and ffprocess.poll() != None):
            global running
            running = "Problem"
        status="None"
        if previewing:
            status="Previewing"
        if streaming:
            status="Recording"
        client.publish("recorder/heartbeat", sensorName + "," + IPAddr + "," + status + "," + running)
    elif (messagePart[0] in "reboot"):
        print("Reboot Requested")
        if (messagePart[1] in sensorName):
            if (streaming):
                stop_streaming()
            os.system("sudo reboot")
    elif (messagePart[0] in "shutdown"):
        print("Shutdown Requested")
        if (streaming):
            stop_streaming()
        os.system("sudo halt")
    elif (messagePart[0] in "update"):
        print("Updating Software")
        os.system("git pull origin master")
        print("Software Updated")
        if (streaming):
            stop_streaming()
        os.system("sudo reboot")
    elif (messagePart[0] in "preview"):
        if (not streaming and not previewing):
            start_previewing()
        else:
            print("Already streaming or previewing")
    elif (messagePart[0] in "stop_preview"):
        if (not streaming and previewing):
            stop_previewing()
        else:
            print("Nor previewing or streaming")
    elif (messagePart[0] in "sensor_preview"):
        if (messagePart[1] in sensorName):
            if (not streaming and not previewing):
                start_previewing()
            else:
                print("Already streaming or previewing")
    elif (messagePart[0] in "sensor_preview_stop"):
        if (messagePart[1] in sensorName):
            if (not streaming and previewing):
                stop_previewing()
            else:
                print("Nor previewing or streaming")
    elif (messagePart[0] in "sensor_shutdown"):
        if (messagePart[1] in sensorName):
            if (streaming):
                stop_streaming()
            os.system("sudo halt")



client = mqtt.Client()
while(True):
    try:
        client.connect(ipMqttServer, int(portMqttServer), 60)
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_forever()
    except:
        time.sleep(1)
