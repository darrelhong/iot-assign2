import serial
import argparse
import random
import time

import paho.mqtt.client as mqtt

from db import get_db

TOPIC = "/fireeyeofthetiger"
POLL_INTERVAL = 3 * 60  # 3 minutes

# store mqtt messages to be processed
message_cache = []


# serial helpers
def sendCommand(command):
    print("send: " + command)
    command = command + "\n"
    ser.write(str.encode(command))


def waitResponse():
    response = ser.readline()
    response = response.decode("utf-8").strip()
    print("resp: " + response)
    return response


# mqtt helpers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code {:d}".format(rc))


def on_message(client, userdata, msg):
    message_cache.append(msg.payload.decode().strip())
    # print("Received '{}' from {} topic".format(msg.payload.decode(), msg.topic))


# sql helpers
def insert_sensor_data(conn, device, temp, light_level):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO edge(device, temp, light_level) VALUES(?, ?, ?)",
        [device, temp, light_level],
    )
    conn.commit()


def insert_fire_event(conn, station_name):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events(station, event_name) VALUES(? , 'Fire outbreak')",
        [station_name],
    )
    conn.commit()


parser = argparse.ArgumentParser()
parser.add_argument(
    "--port",
    help="Microbit serial port",
    type=str,
    default="/dev/ttyACM0",
)
parser.add_argument("--station", help="Edge station name", type=str, default="alpha")
parser.add_argument("--temp", help="Temperature threshold", type=int, default=30)
parser.add_argument("--light", help="Light level threshold", type=int, default=50)
args = parser.parse_args()
STATION_NAME = args.station
TEMP_THRESHOLD = args.temp
LIGHT_THRESHOLD = args.light

conn = get_db()

try:
    # mqtt
    client_id = f"python-mqtt-{random.randint(0, 10000)}"
    client = mqtt.Client(client_id)
    client.username_pw_set("emqx", "public")
    client.on_connect = on_connect
    client.connect("broker.emqx.io", 1883)
    client.subscribe(TOPIC)
    client.on_message = on_message
    client.loop_start()

    # serial
    ser = serial.Serial(port=args.port, baudrate=115200)
    print("Listening serial on {}".format(args.port))

    sendCommand(f"{STATION_NAME} handshake")

    print("waiting for response")
    strMicrobitDevices = ""
    while strMicrobitDevices == None or len(strMicrobitDevices) <= 0:
        strMicrobitDevices = waitResponse()
        time.sleep(0.1)

    strMicrobitDevices = strMicrobitDevices.split("=")

    if len(strMicrobitDevices[1]) > 0:
        listMicrobitDevices = strMicrobitDevices[1].split(",")
        if len(listMicrobitDevices) > 0:
            for mb in listMicrobitDevices:
                print("Connected to micro:bit device {}...".format(mb))

            pollTime = float("-inf")
            while True:
                if not pollTime or time.time() - pollTime > POLL_INTERVAL:
                    sendCommand(f"{STATION_NAME} poll")
                    pollTime = time.time()

                    print("waiting for response")
                    responses = ""
                    while responses == None or len(responses) <= 0:
                        responses = waitResponse()
                        time.sleep(0.1)

                    responses = responses.split(",")

                    for response in responses:
                        values = response.split("-")
                        temp = int(values[1])
                        light_level = int(int(values[2]) / 255 * 100)
                        insert_sensor_data(conn, values[0], temp, light_level)

                        if temp > TEMP_THRESHOLD and light_level > LIGHT_THRESHOLD:
                            sendCommand(f"{STATION_NAME} fire")
                            insert_fire_event(conn, STATION_NAME)

                while message_cache:
                    message = message_cache.pop().strip()
                    message_arr = message.split(" ")
                    if message_arr[1] == "fire":
                        sendCommand(message)
                    elif message_arr[1] == "reset":
                        sendCommand(message)

                time.sleep(0.1)

    else:
        print("No nodes found")

# while True:
#     a = 1
#     msg = ser.readline().decode("utf-8").strip()
#     print(msg)

except serial.SerialException as err:
    print("SerialException: {}".format(err))

except KeyboardInterrupt:
    print("Program Terminated")