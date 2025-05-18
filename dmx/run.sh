#!/bin/bash

# Start OLA
/usr/bin/olad -l 3 > /dev/null 2>&1 &

# Wait a bit for OLA to start
sleep 3

# Start dmx2mqtt (customize with env vars if needed)
python3 /app/bridge.py