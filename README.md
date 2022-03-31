# Instructions

## Installing

* Install RaspiOS
* On configuration update packages
```
pip install paho-mqtt
pip install ffmpeg-python 
pip install pyusb
git clone https://github.com/xaoch/CollaborationRecorder2.git  
```

* Configure the recorder.  Go to the CollaborationRecorder2 folder and do
```
mkdir config
cp config.ini config/config.ini
```

* Activate legacy video
  * Run sudo raspi-config.
  * Navigate to Interface Options and select Legacy camera to enable it.
  * Reboot your Raspberry Pi again.

* Install nginx server
```
sudo apt-get install nginx libnginx-mod-rtmp 
sudo apt-get install nginx-extras
sudo systemctl start nginx.service
sudo systemctl status nginx.service 
sudo nano /etc/nginx/rtmp.conf
```
In that file, just add:
```
rtmp {
  server {
    listen 1935;
    chunk_size 4096;
    application live {
      live on;
      record off;
      sync 10ms;
    }
  }
}
```
with the following line (the location in the file is not important):
```
include /etc/nginx/rtmp.conf;
 ```
Now open the nginx default site configuration:
```
sudo nano /etc/nginx/sites-enabled/default
```
change the root directory
```
root /path/to/the/recordings/folder;
```
and in the location section add:
```
fancyindex      on;
fancyindex_name_length  255;
fancyindex_localtime    on;
fancyindex_exact_size   off;
```
Then we restart the nginx server:
```
sudo systemctl stop nginx.service
sudo systemctl start nginx.service
sudo systemctl status nginx.service
```

Run this script twice to configure the speaker amplifier (see here: https://learn.adafruit.com/adafruit-speaker-bonnet-for-raspberry-pi/raspberry-pi-usage):
Choose always yes.
```
curl -sS https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2samp.sh | bash
```

Install the text to speech software
```
sudo apt-get install espeak
sudo apt-get install sox

espeak "Hello" -w testHello.wav
sox testHello.wav Hello2.wav channels 2 fs 44100
aplay -D pcm.dmixer Hello2.wav
```

Set the script as a service
```
sudo nano /lib/systemd/system/recorder.service
```

Then add:
```
[Unit]
Description=Collaboration Recorder Program
After=network-online.target

[Service]
WorkingDirectory=/home/pi/Code/CollaborationRecorder2
User=pi
ExecStart=python /home/pi/Code/CollaborationRecorder2/main.py /home/pi/Code/CollaborationRecorder2/config.ini

[Install]
WantedBy=multi-user.target
```
Run
```
sudo systemctl daemon-reload
sudo systemctl enable recorder.service
sudo reboot
```





Configure the default sound.  Look available cards:
```
cat /proc/asound/cards
```

You should get something like
```
 0 [Headphones     ]: bcm2835_headpho - bcm2835 Headphones
                      bcm2835 Headphones
 1 [ArrayUAC10     ]: USB-Audio - ReSpeaker 4 Mic Array (UAC1.0)
                      SEEED ReSpeaker 4 Mic Array (UAC1.0) at usb-0000:01:00.0-1.2, full speed
```
Add the Respeaker Array as default
```
sudo nano /etc/asound.conf
```
and add:
```
defaults.pcm.card 1
defaults.ctl.card 1
```

ffmpeg  -thread_queue_size 1024 -video_size 1920x1280 -input_format h264 -i /dev/video0 -thread_queue_size 1024\
        -f alsa -async 1 -channels 1 -sample_rate 44100 -i "sysdefault" \
        -map 0:v -map 1:a -vcodec copy "test.mp4" 

ffmpeg  -thread_queue_size 1024 -video_size 1080x1080 -input_format h264 -i /dev/video0 -thread_queue_size 1024\
        -f alsa -async 1 -channels 1 -sample_rate 44100 -i "sysdefault" \
        -f tee -map 0:v -map 1:a -acodec aac -vcodec copy "test.mp4|[f=flv]rtmp://localhost:1935/live/1"

