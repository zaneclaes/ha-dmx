#!/bin/bash

# Start OLA
/usr/sbin/olad -l

# Wait a bit for OLA to start
sleep 3

# Start dmx2mqtt (customize with env vars if needed)
dmx2mqtt --dmx.device /dev/serial/by-id/usb-ENTTEC_DMX_USB_PRO_EN467365-if00-port0 --mqtt.host $MQTT_HOST