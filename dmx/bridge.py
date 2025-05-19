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

UNIVERSE = 1
DMX_SIZE = 512
BYTES_PER_LIGHT = 4
NUM_LIGHTS = int(DMX_SIZE / BYTES_PER_LIGHT)
data = array.array('B', [0] * DMX_SIZE)
dmx_state = {}

with open('/data/options.json', 'r') as f:
    options = json.load(f)

# MQTT config
mqtt_host = options.get('mqtt_host') # os.environ.get("MQTT_HOST", "core-mosquitto")
mqtt_port = int(options.get('mqtt_port')) # int(os.environ.get("MQTT_PORT", "1883"))
mqttc = mqtt.Client(protocol=mqtt.MQTTv5)

mqtt_user = options.get('mqtt_user') # os.environ.get("MQTT_USER", "dmx")
mqtt_password = options.get('mqtt_password') # os.environ.get("MQTT_PASSWORD", "test1234")
mqttc.username_pw_set(mqtt_user, mqtt_password)

wrapper = ClientWrapper()
ola = wrapper.Client()

def send_dmx(light_num, r, g, b, brightness):
    dmx_state[light_num] = {
        "state": "ON" if brightness > 0 else "OFF",
        "brightness": brightness,
        "rgb_color": [r, g, b]
    }
    print(f'Updating Light #{light_num}: {json.dumps(dmx_state[light_num])}')
    channel_start = ((light_num - 1) * BYTES_PER_LIGHT) + 1
    data[channel_start] = int(brightness)
    data[channel_start + 1] = int(r)
    data[channel_start + 2] = int(g)
    data[channel_start + 3] = int(b)

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
            "rgb": True
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
                send_dmx(light_num, 0, 0, 0, 0)
                return

            brightness = payload.get("brightness", 255)
            r, g, b = payload.get("rgb_color", [255, 255, 255])
            send_dmx(light_num, r, g, b, brightness)
        # if topic_parts[1] == "set":  # dmx/set/<channel>
        #     channel = int(topic_parts[2])
        #     value = int(msg.payload)
        #     data[channel] = value
        #     send_dmx()

        # elif topic_parts[1] == "rgb":  # dmx/set/rgb/<base_channel>
        #     base = int(topic_parts[2])
        #     payload = msg.payload.decode()
        #     # Accept both comma-separated or JSON string formats
        #     if ',' in payload:
        #         r, g, b = map(int, payload.strip().split(','))
        #     else:
        #         import json
        #         rgb = json.loads(payload)
        #         r, g, b = rgb['r'], rgb['g'], rgb['b']
        #     data[base + 1] = r
        #     data[base + 2] = g
        #     data[base + 3] = b
        #     send_dmx()
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