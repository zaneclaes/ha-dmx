print("MQTT startup...")

import sys
print(sys.path)
sys.path.append('/usr/local/lib/python3.9/site-packages')

import array
import paho.mqtt.client as mqtt
from ola.ClientWrapper import ClientWrapper
import os

UNIVERSE = 1
DMX_SIZE = 512
data = array.array('B', [0] * DMX_SIZE)
wrapper = ClientWrapper()
client = wrapper.Client()

# MQTT config
mqtt_host = os.environ.get("MQTT_HOST", "core-mosquitto")
mqtt_port = int(os.environ.get("MQTT_PORT", "1883"))
mqttc = mqtt.Client(protocol=mqtt.MQTTv5)

mqtt_user = os.environ.get("MQTT_USER", "dmx")
mqtt_password = os.environ.get("MQTT_PASSWORD", "test1234")
mqttc.username_pw_set(mqtt_user, mqtt_password)

def send_dmx():
    client.SendDmx(UNIVERSE, data, lambda state: None)

def on_mqtt_message(client_mqtt, userdata, msg):
    print(f'{msg.topic}: {msg.payload}')
    topic_parts = msg.topic.split('/')
    try:
        if topic_parts[1] == "set":  # dmx/set/<channel>
            channel = int(topic_parts[2])
            value = int(msg.payload)
            data[channel] = value
            send_dmx()

        elif topic_parts[1] == "rgb":  # dmx/set/rgb/<base_channel>
            base = int(topic_parts[2])
            payload = msg.payload.decode()
            # Accept both comma-separated or JSON string formats
            if ',' in payload:
                r, g, b = map(int, payload.strip().split(','))
            else:
                import json
                rgb = json.loads(payload)
                r, g, b = rgb['r'], rgb['g'], rgb['b']
            data[base + 1] = r
            data[base + 2] = g
            data[base + 3] = b
            send_dmx()
    except Exception as e:
        print("MQTT parse error:", e)


def on_connect(client, userdata, flags, reasonCode, properties):
    print("MQTT connected")

mqttc.on_connect = on_connect
mqttc.connect(mqtt_host, mqtt_port, 60)
mqttc.on_message = on_mqtt_message
mqttc.subscribe("dmx/set/+")
mqttc.subscribe("dmx/rgb/+")

print("MQTT connecting...")
mqttc.loop_start()

wrapper.Run()