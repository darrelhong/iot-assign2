import random
import time

import paho.mqtt.client as mqtt

TOPIC = "/fireeyeofthetiger"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code {:d}".format(rc))


def run():

    try:
        client_id = f"python-mqtt-{random.randint(0, 10000)}"
        client = mqtt.Client(client_id)
        client.username_pw_set("emqx", "public")
        client.on_connect = on_connect
        client.connect("broker.emqx.io", 1883)

        client.loop_start()

        msg_count = 0

        while True:
            time.sleep(1)

            msg = input("Enter command: ")
            result = client.publish(TOPIC, msg)
            # result: [0, 1]
            status = result[0]

            if status == 0:
                print("Sent '{}' to topic {}".format(msg, TOPIC))
            else:
                print("Failed to send message to topic {}".format(TOPIC))

    except KeyboardInterrupt:

        print("Program terminated!")


if __name__ == "__main__":

    run()
