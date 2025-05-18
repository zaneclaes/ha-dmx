#!/usr/bin/with-contenv bashio

# Load config
DMX_PORT=$(bashio::config 'serial_port')
MQTT_HOST=$(bashio::config 'mqtt_host')
MQTT_PORT=$(bashio::config 'mqtt_port')
MQTT_USER=$(bashio::config 'mqtt_username')
MQTT_PASS=$(bashio::config 'mqtt_password')

echo "Starting DMX2MQTT on $DMX_PORT with MQTT $MQTT_HOST:$MQTT_PORT"
exec python3 main.py --serial "$DMX_PORT" --mqtt-host "$MQTT_HOST" --mqtt-port "$MQTT_PORT" --mqtt-user "$MQTT_USER" --mqtt-password "$MQTT_PASS"