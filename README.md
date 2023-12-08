# barbie-drive-in

Barbie drive-in movie player with web interface and RGB LED running on a raspberry pi. See a video [here](https://youtube.com/shorts/A50qRGPbNX4?si=ZDVCf9kBQVxrtQJw)

## Wifi setup

- Load the raspberry pi's SD card on your computer
- In the root directory of the SD card, look for `wpa_supplicant.conf`
- If it is there, modify the SSID, password, key management, and country code to match your Wifi network
- Otherwise copy the file from this repository into the root directory edited to match your Wifi network
- Replace the SD card in the raspberry pi and turn it on. Leave for ~ 5 minutes to allow to establish a connection
- You should be able to see it on your local network (e.g. through the router's client list) with the hostname `barbie-drive-in`

## Web interface

- you can control playback via the web interface at http://barbie-drive-in.local/
- you can also control the LED behaviour under the settings menu
- port: 80


## Credentials

- default raspberry pi credentials are configured

Username: `pi`
Password: `raspberry`

- do not expose the instance to the Internet

## Accessing

This instance can be accessed via SSH (command line) or VNC (GUI).

## Installation

Run setup script: 
```bash
cd ~/barbie-drive-in
sudo ./setup.sh
```

This will install python requirements and the service to run the web app.

## Configuring the screen and backlight behaviour

You can modify screen rotation in `/boot/config.txt`:

Change the rotation angle `90` to the desired value in the following line: 
```
dtoverlay=waveshare35c:rotate=90
```

Note that the backlight is configured to turn off immediately after starting. To change this behaviour comment out the line in `/boot/config.txt`
```
gpio=18=op,dl
```

## Debugging

You can monitor logs of the web app with `journalctl -u web_app`. Press `shift+G` to go to the end of the log. Press `q` to quit

## Reboot and Shutdown 

Commands can be accessed in the web interface under settings

Alternatively ssh in and issue:
- Reboot: `sudo reboot now`
- Shutdown: `sudo shutdown now`

## Hardware

- Raspberry Pi: Running on Rpi Zero 2W
  - Wasn't able to get display to show GUI on Rpi Zero W but not sure if was an issue with the RPi itself or a configuration issue
- Display: Uses Waveshare 3.5in LCD (C). Running Waveshare drivers.
  - Jumper soldered together on rear as per Waveshare instructions to enable backlight control.
- LED: duinotech 5050 RGB LED module. Any RGB LED with current-limiting resistor will do.
  - pins (duinotech - rpi GPIO): `R : 21, G : 16, B : 20, - : GND`

## Barbie font and favicons

The font and favicons used in the video were purchased from [here](https://www.etsy.com/listing/1516170568/retro-dolly-font-svg-otf-ttf-canva). Place any fonts and favicons you choose in the `static` folder and cross reference in the HTML template. 

