#!/bin/bash
set -ueo pipefail

echo "--- ola ---"

# Start OLA
olad -l 4 &

# Wait a bit for OLA to start
sleep 3

ola_dev_info

netstat -tlnp | grep 9090

# ola_patch -d 0 -u 1

echo "--- bridge ---"

# Start dmx2mqtt (customize with env vars if needed)
python3 -u /app/bridge.py