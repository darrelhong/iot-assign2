import time
from gpiozero import MCP3008

from Adafruit_BME280 import *

divider = MCP3008(0)
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

while True:
    print("light_level" + str(divider.value))
    print("temp" + str(sensor.read_temperature()))
    time.sleep(1)

