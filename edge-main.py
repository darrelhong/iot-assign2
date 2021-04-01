import serial
import argparse
import random
import time
from datetime import datetime
import requests
import paho.mqtt.client as mqtt

from Adafruit_BME280 import *
from db import get_db


TOPIC = "/fireeyeofthetiger"
# 3 minutes 3 * 60  = 180
# 1 minutes 1 * 60 = 60


# store mqtt messages to be processed
message_cache = []

conn = get_db()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--port",
    help="Microbit serial port",
    type=str,
    default="/dev/ttyACM0",
)
parser.add_argument("--station", help="Edge station name", type=str, default="alpha")
parser.add_argument("--temp", help="Temperature threshold", type=int, default=40)
parser.add_argument("--light", help="Light level threshold", type=int, default=80)
parser.add_argument(
    "--cloudhost",
    help="Cloud server hostname",
    type=str,
    default="http://localhost:5001",
)
parser.add_argument(
    "--pollinterval",
    help="Interval in seconds to poll nodes",
    type=int,
    default=60,
)
parser.add_argument(
    "--postinterval",
    help="Interval in seconds to send data to cloud server",
    type=int,
    default=180,
)
parser.add_argument("--rpi", help="Enable if using rpi", action="store_true")
parser.add_argument("--ser", help="Enable if using serials", action="store_true")
args = parser.parse_args()
STATION_NAME = args.station
TEMP_THRESHOLD = args.temp
LIGHT_THRESHOLD = args.light
CLOUD_HOST = args.cloudhost
POLL_INTERVAL = args.pollinterval
POST_INTERVAL = args.postinterval
SERIAL = args.ser

status_led = None
sensor = None

if args.rpi:
    from gpiozero import PWMLED, MCP3008

    status_led = PWMLED(24)

    sensor = BME280(
        t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8
    )
    light_sensor = MCP3008(0)

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


def insert_fire_event(conn, station_name, event, time):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events(station, event_name, time_recorded) VALUES(?,?,?)",
        [station_name, event, time],
    )
    conn.commit()


# request helpers
def send_event_cloud(station_name, event, time):
    try:
        requests.post(
            f"{CLOUD_HOST}/api/events/add",
            json={
                "station": "alpha",
                "event_name": "fire outbreak",
                "time_recorded": time,
            },
        )
    except requests.exceptions.RequestException:
        pass


def send_values_cloud(conn):
    cur = conn.execute("SELECT * FROM edge WHERE sent_to_cloud = 0")
    rv = cur.fetchall()
    cur.close()
    result = [dict(item, station=STATION_NAME) for item in rv]
    try:
        r = requests.post(f"{CLOUD_HOST}/api/sensors/add", json={"rows": result})
        if r.text == "Success":
            cur = conn.execute(
                "UPDATE edge SET sent_to_cloud = 1 WHERE sent_to_cloud = 0"
            )
            conn.commit()
            cur.close()
    except requests.exceptions.RequestException:
        pass


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
    if SERIAL:
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
    postTime = float("-inf")
    while True:
        if time.time() - pollTime > POLL_INTERVAL:
            pollTime = time.time()
            responses = ""

            if SERIAL:
                sendCommand(f"{STATION_NAME} poll")
                print("waiting for response")
                while responses == None or len(responses) <= 0:
                    responses = waitResponse()
                    time.sleep(0.1)

            responses = responses.split(",")
            if args.rpi:
                rpi_temp = round(sensor.read_temperature())
                rpi_light_level = round(light_sensor.value * 100)
                responses.append(f"edge_rpi-{rpi_temp}-{rpi_light_level}")

            for response in responses:
                values = response.split("-")
                if len(values) == 3:
                    temp = int(values[1])
                    light_level = int(int(values[2]) / 255 * 100) if not values[0].startswith('edge') else values[2]
                    insert_sensor_data(
                        conn, f"{STATION_NAME} {values[0]}", temp, light_level
                    )

                    if temp > TEMP_THRESHOLD and light_level > LIGHT_THRESHOLD:
                        print("fire outbreak detected")
                        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        event = "fire outbreak"
                        SERIAL and sendCommand(f"{STATION_NAME} fire")
                        insert_fire_event(conn, STATION_NAME, event, curr_time)
                        send_event_cloud(STATION_NAME, event, curr_time)

        while message_cache:
            try:
                message = message_cache.pop().strip()
                message_arr = message.split(" ")
                station = message_arr[0]
                command = message_arr[1]
                message
                if command == "fire":
                    insert_fire_event(
                        conn,
                        station,
                        "fire outbreak",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    SERIAL and sendCommand(message)
                    if station == STATION_NAME:
                        status_led and status_led.on()
                    else:
                        status_led and status_led.blink(0.5, 0.5)
                elif command == "reset":
                    SERIAL and sendCommand(message)
                    status_led and status_led.off()
            except IndexError:
                print("Error processing message")

        if time.time() - postTime > POST_INTERVAL:
            postTime = time.time()
            print("sending values to cloud")
            send_values_cloud(conn)

        time.sleep(0.1)


# while True:
#     a = 1
#     msg = ser.readline().decode("utf-8").strip()
#     print(msg)

except serial.SerialException as err:
    print("SerialException: {}".format(err))

except KeyboardInterrupt:
    print("Program Terminated")
