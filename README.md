# System Configuration Variables:

* set the followin variables in the `Fleet Configuration` application side tab
  - `RESIN_HOST_CONFIG_dtoverlay` = `hifiberry-dac`


* `NGROK_AUTH` : If you want to manage your ngrok tunnel the ngrok interface.
* `NGROK_REGION` : the region you want your tunnel to go through.
* `SPOTIFY_USER` : Your user name on spotify (**NB:** Needs to be premium account)
* `SPOTIFY_PASS` : password for the spotify user above.

# TODO:

## General Structure:
* add a queue to share data between threads

## Music Related:
* ~~ serve the webUI over ngrok channel ~~
* ~~ point cache files to /data ~~
* ~~ move to external audio (pHat) ~~
* ~~ create a `shaunmulligan/mopidy` base image ~~
* create a state/flow diagram
* ~~ control player via https://github.com/ismailof/mopidy-json-client ~~
  * ~~ need to check that mopidy is ready~~
	* ~~ Should allow play/pause and next track functions~~
  * ~~ need to be able to check current state.~~
* ~~ print grok URL on dashboard using: https://github.com/peakwinter/python-ngrok ~~
* get events from mopidy websocket (??)
* add a timeout in "Alive check" incase mopidy never starts up
* better exception handling when loading playlist, etc.
* perhaps use [alsamixer] option to select which audio card to use.
* mount SDcard in modem to `/mnt/music` if it exists and allow mopidy to read from that location for local music
* ~~ [failed] look at improving sound output by following: http://forums.pimoroni.com/t/howto-get-phat-dac-to-play-all-system-sound-software-volume-control/2361 ~~
* figure out why https causes issues. (it seems because the websocket they use is not secure, i.e: wss instead of ws)
* figure out how to make the Iris port default to 80 instead of 6680 (https://github.com/jaedb/Iris)
* broadcast the grok URL using pyeddystone example.
* add `dtoverlay=i2s-mmap` to config.txt
* Huawei E3131 http://hi.link == 192.168.8.1
  * get signal strength

## Input:
* Mode Selection:
  * music control
  * volume control
* control music playback functionality via GPIO
  * ~~ next_track ~~
  * ~~ toggle (play/pause) ~~
* control volume
  * up
  * down
* GPS session:
  * start
  * stop

## GPS related:
* ~~ get A-GPS working on Ultimate GPS Hat.~~
  * https://github.com/f5eng/mt3339-utils
* ~~ Figure out how to discover/probe the GPS tty port.~~ Not needed
* ~~ be able to read NMEA sentences from the GPS port.~~
* ~~ convert nmea to GPX track (https://gist.github.com/ppearson/52774)~~
* be able to detect if the device has a Fix or not. (need to pull this out of nmea sentence)
* ~~ write the NMEA sentences to a file in `/data` with a time stamp of when the run started. I think as a `.gpx` file which Strava can consume ~~
  * https://pypi.python.org/pypi/gpxpy/0.8.8
* ~~ draw a gpx track on google maps with JS: https://github.com/peplin/gpxviewer ~~ Use strava instead
* Fix errors with synchronising GPS uart baud rate and failure to write EPO file.
* ~~ Add coin battery to improve TTFF. ~~
* Use resin.io dashboard location to feed first location Configuration
* custom GPS location to the resin.io dashboard:
  `curl 'https://api.resinstaging.io/v2/device(54327)' -X PATCH -H 'Authorization: Bearer BEARER_TOKEN' -H 'Content-Type: application/json;charset=UTF-8' --data-binary '{"custom_latitude":"51.5074603461279","custom_longitude":"-2.6978302001953125"}' —compressed`
* periodically (10seconds?) convert nmea file into GPX and extract info using https://github.com/tkrajina/gpxpy:
  * Distance
  * average pace
  * moving time
* extract GPS fix quality from NMEA with https://github.com/Knio/pynmea2

## Output
* ~~four RBG neopixels to indicate status:~~ neopixels require the same gpio as i2s audio :/
* 128*64 OLED LCD with i2c interface:
  * GPS Fix
  * Current Song
  * Distance
  * levels:
    * 3G signal level
    * volume level
    * battery level (maybe)
* Vibro haptic output:
  * warnings
  * when GPS locks/fix
  * every 1km

## Misc:
* Implement battery level checking
* hold update lock while running or listening to music.
* ~~ clean up dockerfile and move wget and pyserial into Dockerfile.prebuild ~~
* Network: make sure its possible to enable or disable wlan0 so modem is not always the primary connection.
* ~~ test performance on rpi zero. ~~
* Power Consumption test: (looks like rpi zero can do about 3 hours running music + gps on modem)
  * rpiZero = 140ma, try disable HDMI too: https://www.jeffgeerling.com/blogs/jeff-geerling/raspberry-pi-zero-conserve-energy, perhaps try: “hdmi_blanking=2” > config.txt (https://github.com/raspberrypi/firmware/issues/352) https://github.com/retropie/retropie-setup/wiki/Overclocking
  * modem = 270mah
  * ultimate GPS =  20 mA during navigation
  * phat Dac = ?
  * total = ?

## Hardware:
* create circuit diagram
* figure out how to measure battery levels
  * use ADS1x15 if there is space in the enclosure
* figure out how to mount the SIM card with Huawei E3131 module

## Optimisation
* remove alsa-utils (??)
* possibly remove libav

import pynmea2
msg = pynmea2.parse("$GPGGA,173004.000,5132.2394,N,00002.7293,W,2,09,0.90,26.1,M,47.0,M,0000,0000*4E")
