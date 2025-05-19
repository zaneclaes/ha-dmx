#!/bin/bash
# set -ueo pipefail

echo "--- ola ---"

# Start OLA
olad -l 1 &

# Wait a bit for OLA to start
sleep 3

echo "--- devices ---"
ola_dev_info

# ola_patch -d 0 -u 1

echo "--- bridge ---"

# Start dmx2mqtt (customize with env vars if needed)
python3 -u /app/bridge.py