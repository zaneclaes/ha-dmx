print("MQTT startup...")

import sys
print(sys.path)
sys.path.append('/usr/local/lib/python3.9/site-packages')

import array
import time
import json
import paho.mqtt.client as mqtt
from ola.ClientWrapper import ClientWrapper
import os
import math
from dmx import DmxLight

UNIVERSE = 1
DMX_SIZE = 512
data = array.array('B', [0] * DMX_SIZE)

with open('/data/options.json', 'r') as f:
    options = json.load(f)

print(options)

BYTES_PER_LIGHT = options.get('light_bytes')
NUM_LIGHTS = int(math.floor(DMX_SIZE / BYTES_PER_LIGHT))

# MQTT config
mqtt_host = options.get('mqtt_host') # os.environ.get("MQTT_HOST", "core-mosquitto")
mqtt_port = int(options.get('mqtt_port')) # int(os.environ.get("MQTT_PORT", "1883"))
mqttc = mqtt.Client(protocol=mqtt.MQTTv5)

mqtt_user = options.get('mqtt_user') # os.environ.get("MQTT_USER", "dmx")
mqtt_password = options.get('mqtt_password') # os.environ.get("MQTT_PASSWORD", "test1234")
mqttc.username_pw_set(mqtt_user, mqtt_password)

wrapper = ClientWrapper()
ola = wrapper.Client()

lights = {}

def send_bytes():
    ola.SendDmx(UNIVERSE, data, lambda state: None)

def write_byte(idx, val):
    data[idx - 1] = val # In reality, everything is zero-indexed, but channel names are 1-indexed

def set_light_state(light, payload):
    if 'brightness' in payload:
        light.set_brightness(payload.get("brightness", 255))
    if 'state' in payload:
        state = payload.get('state')
        if state == "ON":
            if light.state['brightness'] == 0:
                light.set_brightness(255)
        if state == "OFF" and light.state['brightness'] > 0:
            light.set_brightness(0)
    if 'color' in payload:
        col = payload.get("color")
        light.set_rgb(col['r'], col['g'], col['b'])
    send_bytes()
    light.publish_state()

def on_mqtt_message(client_mqtt, userdata, msg):
    # print(f'{msg.topic}: {msg.payload}')
    parts = msg.topic.split('/')

    # try:
    light = lights[parts[1]]
    if not light:
        print(f'Missing light: {parts[1]}')
    elif parts[2] == 'set':
        set_light_state(light, json.loads(msg.payload.decode()))
    elif parts[2] == 'attribute':
        light.set_attribute(parts[3], msg.payload)
        send_bytes()
        light.publish_attributes()
    # except Exception as e:
    #     print("MQTT parse error:", e)

def on_connect(client, userdata, flags, reasonCode, properties):
    print("MQTT connected")
    for data in options.get('lights'):
      lights[data['name']] = DmxLight(data, mqttc, write_byte)

mqttc.on_connect = on_connect
mqttc.connect(mqtt_host, mqtt_port, 60)
mqttc.on_message = on_mqtt_message
mqttc.subscribe("dmx/+/set")
mqttc.subscribe("dmx/+/attribute/+/set")

print(f"MQTT connecting to {mqtt_host}...")
mqttc.loop_start()

wrapper.Run()