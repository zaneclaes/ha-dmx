#!/bin/bash

ls /dev/ttyUSB*
ls -l /dev/serial/by-id/

# Start OLA
/usr/bin/olad -l 3 > /dev/null 2>&1 &

# Wait a bit for OLA to start
sleep 3

ola_dev_info

ola_patch -d 0 -u 1

# Start dmx2mqtt (customize with env vars if needed)
python3 -u /app/bridge.py