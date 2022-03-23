# Instructions

## Installing

* Install RaspiOS
* On configuration update packages
```
pip install paho-mqtt
pip install ffmpeg-python 
git clone https://github.com/xaoch/CollaborationRecorder2.git  
```
* Activate legacy video
  * Run sudo raspi-config.
  * Navigate to Interface Options and select Legacy camera to enable it.
  * Reboot your Raspberry Pi again.

* Install ngix server
```
sudo apt-get install nginx libnginx-mod-rtmp
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
autoindex on;
```
Then we restart the nginx server:
```
sudo systemctl stop nginx.service
sudo systemctl start nginx.service
sudo systemctl status nginx.service
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


