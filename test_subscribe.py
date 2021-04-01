import random

import paho.mqtt.client as mqtt


def on_connect(client, usedata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("failed to connect")

def on_message(client, userdata, msg):
    print("Received '{}' from topic '{}'".format(msg.payload.decode(), msg.topic))

try:
    client_id = f"python-mqtt-{random.randint(0, 10000)}"
    client = mqtt.Client(client_id)
    client.username_pw_set("emqx", "public")
    client.on_connect = on_connect
    client.connect("broker.emqx.io", 1883)
    client.subscribe('/fireeyeofthetiger')
    client.on_message = on_message
    client.loop_forever()

except KeyboardInterrupt:
    print("Program Terminated")
