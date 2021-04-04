from gpiozero import PWMLED

status_led = PWMLED(24)

type = int(input("Enter type: "))

if type == 0:
    status_led.on()
elif type == 1:
    status_led.blink(0.5, 0.5)

while True:
    a = 1
