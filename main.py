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

config = configparser.ConfigParser()
config.read(sys.argv[1])

ipMqttServer = config["DEFAULT"]["MQTTServerIp"]
portMqttServer = config["DEFAULT"]["MQTTServerPort"]
sensorName = config["DEFAULT"]["SensorName"]
streaming = False
ffprocess = None
running = "Alive"

print(portMqttServer)
# time.sleep(30)
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname + ".local")
proc=None

def start_streaming(recordingId):
    directoryPath = os.path.join("recordings", recordingId)
    os.mkdir(directoryPath)
    filePath= os.path.join(directoryPath, sensorName+".mp4")
    doaPath=os.path.join(directoryPath, sensorName+"_doa.mp4")
    #audio = ffmpeg.input("sysdefault", f="alsa", channels=1, sample_rate=44100)
    #video = ffmpeg.input("/dev/video0", vf="drawtext=fontfile=roboto.ttf:fontsize=36:fontcolor=yellow:text='%{pts\:gmtime\:1575526882\:%A, %d, %B %Y %I\\\:%M\\\:%S %p}'",f="v4l2", input_format="h264", framerate=15)
    #out1 = ffmpeg.output(audio, video, "rtmp://localhost:1935/live/1", f="flv", vcodec="copy")
    #out2 = ffmpeg.output(audio, video, filePath, vcodec="copy")
    #out = ffmpeg.merge_outputs(out1, out2)
    audio = ffmpeg.input("sysdefault", f="alsa", channels=1, sample_rate=44100)
    video = ffmpeg.input("/dev/video0", f="v4l2", input_format="h264", video_size=(1280, 976), framerate=15)
    text = video.drawtext(textfile="doa.txt", reload=1, fontcolor="red", x=40, y=40, fontsize="64", escape_text=True)
    text = text.split()
    out1 = ffmpeg.output(audio, text[0], "rtmp://localhost:1935/live/1", f="flv", preset="ultrafast")
    out2 = ffmpeg.output(audio, video, filePath, vcodec="copy")
    out3 = ffmpeg.output(text[1], doaPath, preset="ultrafast")
    out = ffmpeg.merge_outputs(out1, out2, out3)
    global ffprocess
    global streaming
    global proc
    proc = subprocess.Popen(['sudo','python', 'doa.py', recordingId])
    ffprocess = ffmpeg.run_async(out)
    streaming = True


def stop_streaming():
    global ffprocess
    global proc
    ffprocess.send_signal(signal.SIGINT)
    ffprocess.wait()
    proc.send_signal(signal.SIGTERM)
    #proc.wait()
    #ffprocess.kill()
    print("Stoping")
    global streaming
    streaming = False


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
    elif (messagePart[0] in "sensorstart"):
        if (messagePart[1] in sensorName):
            if (not streaming):
                recordingId = messagePart[2]
                start_streaming(recordingId)
            else:
                print("Already streaming")
    elif (messagePart[0] in "sensorstop"):
        if (messagePart[1] in sensorName):
            if (streaming):
                stop_streaming()
            else:
                print("Not Streaming")
    elif (messagePart[0] in "report alive"):
        if (streaming and ffprocess.poll() != None):
            global running
            running = "Problem"
        client.publish("recorder/heartbeat", sensorName + "," + IPAddr + "," + str(streaming) + "," + running)
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



client = mqtt.Client()
while(True):
    try:
        client.connect(ipMqttServer, int(portMqttServer), 60)
        client.on_connect = on_connect
        client.on_message = on_message
        client.loop_forever()
    except:
        time.sleep(1)
