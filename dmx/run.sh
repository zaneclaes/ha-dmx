#!/bin/bash

sudo chgrp dmxuser /dev/ttyUSB0
sudo chmod 666 /dev/ttyUSB0
ls /dev/ttyUSB*
ls -l /dev/serial/by-id/

# Start OLA
/usr/bin/olad -l 4 &

# Wait a bit for OLA to start
sleep 3

ola_dev_info
ls /usr/lib/ola/libola*so*
cat /home/dmxuser/.ola/ola-usbserial.conf
ls /usr/lib/ola/ | grep libola_

ola_patch -d 0 -u 1

# Start dmx2mqtt (customize with env vars if needed)
python3 -u /app/bridge.py