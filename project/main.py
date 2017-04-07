#!/usr/bin/env python
# main.py
from __future__ import unicode_literals
from PIL import ImageFont
import signal
import sys, os
import RPi.GPIO as GPIO
from MusicControl import Music
import serial
import threading
import time
import logging
from luma.core.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.virtual import viewport

logging.basicConfig(level=logging.WARNING, format='(%(threadName)-9s) %(message)s',)

# Globals
music = None
ser = None
oled = None
gps_log_flag = threading.Event()
kill_session_flag = threading.Event()
display_mode = 1

def signal_term_handler(signal, frame):

    GPIO.cleanup()
    ser.close()
    logging.warning('got SIGTERM, cleaning up\n')
    oled.cleanup()
    sys.exit(0)

def next_track_callback(channel):
    music.next_track()
    logging.warning("skipping to next track")

def toggle_playback_callback(channel):
    if music.state()["result"] == "paused" or music.state()["result"] == "stopped":
        music.play()
        logging.warning("Starting playback...")
    else:
        music.pause()
        logging.warning("Pausing playback...")

def toggle_gps_callback(channel):
    if gps_log_flag.isSet():
        print("gps_log_flag is True")
        stop_logging()
        stop_gps_log_session()
    else:
        print("gps_log_flag is False")
        start_gps_log_session()
        start_logging()

def start_gps_log_session():
    print("Setup GPS session")
    kill_session_flag.clear()
    f = "/data/gps/nmea" + time.strftime("%Y%m%d-%H%M%S") + ".log"
    open(f, 'a').close()
    gps_thread = threading.Thread(name='gps',
                      target=gps_logger,
                      args=(gps_log_flag,kill_session_flag,f,))
    gps_thread.start()
    return gps_thread

def stop_gps_log_session():
    kill_session_flag.set()

def start_logging():
    print("starting GPS logging")
    gps_log_flag.set()

def stop_logging():
    print("stopping GPS logging")
    gps_log_flag.clear()

def gps_logger(gps_flag, kill_flag, fp):
    while not kill_flag.isSet():
        if gps_flag.isSet() and ser.isOpen():
            data = ser.readline()   # reads in bytes followed by a newline
            logging.info(data)

            with open(fp,"a+") as f:
                f.write(data)
    print("closing GPS logging Session")

def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)

def scroll_message(track, font=None, speed=1):
    try:
        track = music.get_track()
        song_name = track['result']['name']
        artist_name = track['result']['artists'][0]['name']
    except Exception as e:
        song_name = "No Track found"
        artist_name = "none"

    full_text = u"{0} - {1}".format(artist_name, song_name)
    x = oled.width

    # First measure the text size
    with canvas(oled) as draw:
        w, h = draw.textsize(full_text, font)

    virtual = viewport(oled, width=max(oled.width, w + x + x), height=max(h, oled.height))
    with canvas(virtual) as draw:
        draw.text((x, 0), full_text, font=font, fill="white")

    i = 0
    while i < x + w:
        virtual.set_position((i, 0))
        i += speed
        time.sleep(0.025)

def setup():
    global music
    global ser
    global oled
    # Setup Buttons
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    signal.signal(signal.SIGTERM, signal_term_handler)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=next_track_callback, bouncetime=300)
    GPIO.add_event_detect(24, GPIO.FALLING, callback=toggle_playback_callback, bouncetime=300)
    GPIO.add_event_detect(25, GPIO.FALLING, callback=toggle_gps_callback, bouncetime=300)

    # Setup OLED display
    oled_i2c = i2c(port=1, address=0x3C)
    oled = ssd1306(oled_i2c, width=128, height=32)
    font_awesome = make_font("fontawesome-webfont.ttf", oled.height - 12)
    font_code2000 = make_font("code2000.ttf", oled.height - 12)

    # Set up serial for GPS
    ser = serial.Serial()
    ser.port = '/dev/ttyAMA0'
    ser.baudrate = 57600
    ser.timeout = 1

    try:
        ser.open()
    except IOError as err:
        logging.warning("Unable to connect to GPS module: " + err)

    with canvas(oled) as draw:
        music_icon = "\uf001"
        w, h = draw.textsize(text=music_icon, font=font_awesome)
        top = (oled.height - h) / 2
        draw.text((0, top), text=music_icon, font=font_awesome, fill="white")
        draw.text((10, top), text=" TuneTrackr", font=font_code2000, fill="white")

    music = Music()

    return music, oled, ser, font_code2000

def main():
    m, lcd, gps, font = setup()

    logging.warning("=====================================================================================")
    while music.server_alive() == False:
        continue
    logging.warning(music.load_playlist())
    logging.warning("=====================================================================================")
    # Start up the default playlist
    music.play()

    while 1:
        if display_mode == 1:
            try:
                track = music.get_track()
                scroll_message(track, font=font,speed=2)
            except Exception as e:
                print("Couldn't get current track")

            print(m.state())
            time.sleep(0.1)
        else:
            print("Info Mode")

if __name__ == '__main__':
    main()
