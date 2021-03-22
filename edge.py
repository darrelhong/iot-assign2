# demo uart transmit and receive

import time
from bluetooth import ble

import util
from bleuartlib import BleUartDevice


def bleUartReceiveCallback(data):

    print("Received data = {}".format(data))


try:

    bleUartDevice1 = None
    found_microbit = False

    service = ble.DiscoveryService()
    devices = service.discover(2)

    print("********** Initiating device discovery......")

    for address, name in devices.items():

        found_microbit = False

        if address == "CE:E5:E1:2F:81:3E":

            print("Found BBC micro:bit [vavet]: {}".format(address))
            found_microbit = True
            break

    if found_microbit:

        bleUartDevice1 = BleUartDevice(address)
        bleUartDevice1.connect()
        print("Connected to micro:bit device")

        bleUartDevice1.enable_uart_receive(bleUartReceiveCallback)
        print("Receiving data...")

        while True:

            response = input("Do you want to transmit command to micro:bit (Y/n) = ")

            if response == "Y":

                command = input("Enter command to send = ")
                bleUartDevice1.send(command)
                print("Finished sending command...")

            time.sleep(0.1)

except KeyboardInterrupt:

    print("********** END")

except:

    print("********** UNKNOWN ERROR")

finally:

    if bleUartDevice1 != None:
        bleUartDevice1.disconnect()
        bleUartDevice1 = None
        print("Disconnected from micro:bit device")
