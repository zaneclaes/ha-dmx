#!/bin/bash
# set -ueo pipefail

echo "--- ola ---"

# Start OLA
olad -l 1 &

# Wait a bit for OLA to start
sleep 3

echo "--- devices ---"
ola_dev_info

echo "--- universe ---"
CONFIG_FILE="/data/options.json"

DEVICE_NUM=$(jq -r '.device_num' "$CONFIG_FILE")
OUTPUT_PORT=$(jq -r '.output_port' "$CONFIG_FILE")

echo "Creating Universe #1 for Device #${DEVICE_NUM} and Port #${OUTPUT_PORT}"
ola_patch -u 1 -d "${DEVICE_NUM:-2}" -p "${OUTPUT_PORT:-0}"

echo "--- bridge ---"

# Start dmx2mqtt (customize with env vars if needed)
python3 -u /app/bridge.py