#!/bin/bash
set -ueo pipefail

echo "--- ola ---"

# Start OLA
/usr/bin/olad -l 4 &

# Wait a bit for OLA to start
sleep 3

ola_dev_info
ls /usr/lib/ola/libola*so*
cat /home/dmxuser/.ola/ola-usbserial.conf
ls /usr/lib/ola/ | grep libola_

# ola_patch -d 0 -u 1

echo "--- bridge ---"

# Start dmx2mqtt (customize with env vars if needed)
python3 -u /app/bridge.py