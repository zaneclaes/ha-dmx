#!/bin/bash

ola_dev_info

ls /dev/ttyUSB*
ls -l /dev/serial/by-id/

# Start OLA
/usr/bin/olad --dmx-device /dev/dmx > /dev/null 2>&1 &

# Wait a bit for OLA to start
sleep 3

# Start dmx2mqtt (customize with env vars if needed)
python3 -u /app/bridge.py