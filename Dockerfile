FROM shaunmulligan/rpi-jessie-mopidy:v1.1.0

COPY mopidy.conf /etc/mopidy/mopidy.conf

# Set our working directory
WORKDIR /usr/src/app

# Copy all our project into /usr/src/app/ folder in the container.
COPY . .

CMD ["bash","project/startup.sh"]
