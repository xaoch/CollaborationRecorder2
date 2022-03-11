#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import socket
import configparser
import os
import ffmpeg
import sys
import time

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


def start_streaming():
    audio = ffmpeg.input("default", f="alsa", channels=1, sample_rate=44100)
    video = ffmpeg.input("/dev/video0", f="v4l2", input_format="h264", framerate=15)
    out = ffmpeg.output(audio, video, "http://" + IPAddr + ":8080", listen=1, f="flv", vcodec="copy")
    global ffprocess
    global streaming
    ffprocess = ffmpeg.run_async(out)
    streaming = True


def stop_streaming():
    global ffprocess
    ffprocess.kill()
    print("Stoping")
    global streaming
    streaming = False


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("recorder/control")
    client.publish("recorder/heartbeat", sensorName + "," + IPAddr + "," + str(streaming) + "," + running)


def on_message(client, userdata, msg):
    message = msg.payload.decode()
    messagePart = message.split(",")
    if (messagePart[0] in "start"):
        start_streaming()
    elif (messagePart[0] in "stop"):
        stop_streaming()
    elif (messagePart[0] in "sensorstart"):
        if (messagePart[1] in sensorName):
            start_streaming()
    elif (messagePart[0] in "sensorstop"):
        if (messagePart[1] in sensorName):
            stop_streaming()
    elif (messagePart[0] in "report alive"):
        if (streaming and ffprocess.poll() != None):
            global running
            running = "Problem"
        client.publish("recorder/heartbeat", sensorName + "," + IPAddr + "," + str(streaming) + "," + running)
    elif (messagePart[0] in "reboot"):
        print("Reboot Requested")
        if (messagePart[1] in sensorName):
            os.system("sudo reboot")


client = mqtt.Client()
client.connect(ipMqttServer, int(portMqttServer), 60)
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
