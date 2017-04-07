#!/usr/bin/env bash

# Ensure mopidy folders are there
mkdir -p /data/mopidy/local >/dev/null 2>&1 || true
mkdir /data/mopidy/media >/dev/null 2>&1 || true
mkdir /data/mopidy/playlists >/dev/null 2>&1 || true
mkdir /data/mopidy/cache >/dev/null 2>&1 || true

# Change the spotify user creds
if env | grep -q ^SPOTIFY_USER= ; then
  echo "Enabling Spotify and adding its credentials"
  sed -i '/^\[spotify\]$/,/^\[/ s/^enabled = false/enabled = true/' /etc/mopidy/mopidy.conf
  sed -i '/^\[spotify\]$/,/^\[/ s/^username = none/username = '"$SPOTIFY_USER"'/' /etc/mopidy/mopidy.conf
  sed -i '/^\[spotify\]$/,/^\[/ s/^password = none/password = '"$SPOTIFY_PASS"'/' /etc/mopidy/mopidy.conf
  sync
fi

# Launch mopidy daemon with our config
python /usr/bin/mopidy --config /etc/mopidy/mopidy.conf &

# Create GPS data folder and serve it on port 8000
mkdir -p /data/gps/ >/dev/null 2>&1 || true
cd /data/gps
# Only activate the server if we have the env var set
if env | grep -q ^FILE_SERVER= ; then
  echo "Starting fileserver on port 8080"
  python -m SimpleHTTPServer 8080 &
fi
cd -

echo "Will atempt to use external Audio Hat"
echo "NB!!! add the following Variables to your device dashboard config"
echo "{RESIN_HOST_CONFIG_dtoverlay = hifiberry-dac} "
echo "{RESIN_HOST_CONFIG_dtparam = audio=off} "

# force the baudrate to 57600 if it's not already
./project/gpsinit -s 9600 -f /usr/src/app/project/setspeed.conf /dev/ttyAMA0
if [ ! -f /data/MTK14.EPO ]; then
    echo "EPO GPS file not found!"
    ./project/epofetch MTK14.EPO /data/MTK14.EPO
    ./project/epoloader -s 115200 -k @project/loc.conf /data/MTK14.EPO /dev/ttyAMA0
fi

python project/main.py
