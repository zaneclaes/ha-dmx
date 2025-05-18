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
mqttc.username_pw_set("dmx", "test1234")

def on_mqtt_message(client_mqtt, userdata, msg):
    try:
        channel = int(msg.topic.split('/')[-1])
        value = int(msg.payload)
        data[channel] = value
        client.SendDmx(UNIVERSE, data, lambda state: None)
    except Exception as e:
        print("Error:", e)

def on_connect(client, userdata, flags, reasonCode, properties):
    print(f"Connected with reason code: {reasonCode}")

mqttc.on_connect = on_connect
mqttc.connect(mqtt_host, mqtt_port, 60)
mqttc.on_message = on_mqtt_message
mqttc.subscribe("dmx/set/+")
mqttc.loop_start()

wrapper.Run()