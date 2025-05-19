print("MQTT startup...")

import sys
print(sys.path)
sys.path.append('/usr/local/lib/python3.9/site-packages')

import array
import json
import time
import paho.mqtt.client as mqtt
from ola.ClientWrapper import ClientWrapper
import os
import math

UNIVERSE = 1
DMX_SIZE = 512
data = array.array('B', [0] * DMX_SIZE)
dmx_state = {}

with open('/data/options.json', 'r') as f:
    options = json.load(f)


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

def send_dmx(light_num):
    dmx_state[light_num]['state'] = "ON" if dmx_state[light_num]['brightness'] > 0 else "OFF"
    print(f'Updating Light #{light_num}: {json.dumps(dmx_state[light_num])}')
    channel_start = ((light_num - 1) * BYTES_PER_LIGHT)
    data[channel_start] = int(dmx_state[light_num]['brightness'])
    data[channel_start + 1] = int(dmx_state[light_num]['rgb_color'][0])
    data[channel_start + 2] = int(dmx_state[light_num]['rgb_color'][1])
    data[channel_start + 3] = int(dmx_state[light_num]['rgb_color'][2])

    ola.SendDmx(UNIVERSE, data, lambda state: None)
    mqttc.publish(f'dmx/{light_num}/state', json.dumps(dmx_state[light_num]), retain=True)

def publish_config():
    for fixture in range(1, NUM_LIGHTS):  # 3 channels per RGB fixture
        config_topic = f"homeassistant/light/dmx_{fixture}/config"
        mqttc.publish(config_topic, json.dumps({
            "name": f"DMX RGB Light {fixture}",
            "unique_id": f"dmx_{fixture}",
            "schema": "json",
            "command_topic": f"dmx/{fixture}/set",
            "state_topic": f"dmx/{fixture}/state",
            "brightness": True,
            "color_mode": True,
            "supported_color_modes": ["rgb"]
        }), retain=True)
        dmx_state[fixture] = {
            "state": "OFF",
            "brightness": 0,
            "rgb_color": [0, 0, 0]
        }
        mqttc.publish(f'dmx/{fixture}/state', json.dumps(dmx_state[fixture]), retain=True)

def on_mqtt_message(client_mqtt, userdata, msg):
    print(f'{msg.topic}: {msg.payload}')
    parts = msg.topic.split('/')
    try:
        if parts[0] == 'dmx' and parts[2] == 'set':
            light_num = int(parts[1])
            if light_num <= 0 or light_num > NUM_LIGHTS:
                raise f'Invalid light num {light_num}'
            payload = json.loads(msg.payload.decode())

            if payload.get("state", "").upper() == "OFF":
                dmx_state[light_num]['brightness'] = 0
                send_dmx(light_num)
                return

            if 'brightness' in payload:
                dmx_state[light_num]['brightness'] = payload.get("brightness", 255)
            if 'color' in payload:
                col = payload.get("color")
                dmx_state[light_num]['rgb_color'] = [col['r'], col['g'], col['b']]
            send_dmx(light_num)
    except Exception as e:
        print("MQTT parse error:", e)


def on_connect(client, userdata, flags, reasonCode, properties):
    print("MQTT connected")
    publish_config()

mqttc.on_connect = on_connect
mqttc.connect(mqtt_host, mqtt_port, 60)
mqttc.on_message = on_mqtt_message
mqttc.subscribe("dmx/+/set")

print(f"MQTT connecting to {mqtt_host}...")
mqttc.loop_start()

wrapper.Run()