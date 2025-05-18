#!/bin/bash

ls /dev/ttyUSB*
ls -l /dev/serial/by-id/

# Start OLA
/usr/bin/olad --dmx-device /dev/serial/by-id/usb-ENTTEC_DMX_USB_PRO_EN467365-if00-port0 &

# Wait a bit for OLA to start
sleep 3

ola_dev_info

ola_patch -d 0 -u 1

# Start dmx2mqtt (customize with env vars if needed)
python3 -u /app/bridge.py