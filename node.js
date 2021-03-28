radio.setGroup(0)
radio.setTransmitSerialNumber(true)
radio.setTransmitPower(7)
let connected = false
let state = 'base'
const STATION_NAME = 'alpha'


radio.onReceivedString(function (receivedString: string) {
    const [station, command] = receivedString.split(' ')
    if (command == 'reset') {
        basic.clearScreen()
        state = 'base'
    }
    if (station == STATION_NAME) {
        if (command == 'handshake') {
            if (!connected) {
                connected = true
                randomWait()
                radio.sendString('enrol=' + control.deviceName())
            }
        } else {
            if (connected) {
                if (command == 'poll') {
                    randomWait()
                    radio.sendString(`${control.deviceName()}-${input.temperature()}-${input.lightLevel()}`)
                }
                if (command == 'fire') {
                    state = 'fire';
                }
            }
        }
    } else if (command == 'fire') {
        state = 'blink'
    }
})

basic.forever(function () {
    if (state == 'base') {
        plotConnected(connected)
        plotLightLevel(input.lightLevel())
        plotTemperature(input.temperature())
    } else if (state == 'fire') {
        basic.showLeds(`
      # # # # #
      # # # # #
      # # # # #
      # # # # #
      # # # # #
      `)
    } else if (state == 'blink') {
        basic.showLeds(`
      # # # # #
      # # # # #
      # # # # #
      # # # # #
      # # # # #
      `)
        basic.pause(100)
        basic.clearScreen()
        basic.pause(100)
    }
})

input.onButtonPressed(Button.A, function () {
    if (state == 'base') {
        state = 'fire'
    } else if (state == 'fire') {
        state = 'blink'
    } else if (state == 'blink') {
        state = 'base'
    }
})

// helpers
function randomWait() {
    basic.pause(Math.randomRange(100, 4900))
}

function plotConnected(connected: boolean) {
    if (connected) {
        led.plot(4, 0)
        led.plot(4, 1)
        led.plot(4, 2)
        led.plot(4, 3)
        led.plot(4, 4)
    } else {
        led.unplot(4, 0)
        led.unplot(4, 1)
        led.unplot(4, 2)
        led.unplot(4, 3)
        led.unplot(4, 4)
    }
}

function plotLightLevel(level: number) {
    led.unplot(2, 0)
    led.unplot(2, 1)
    led.unplot(2, 2)
    led.unplot(2, 3)
    led.unplot(2, 4)
    if (level > 51) {
        led.plot(2, 4);
    }
    if (level > 102) {
        led.plot(2, 3);
    }
    if (level > 153) {
        led.plot(2, 2);
    }
    if (level > 204) {
        led.plot(2, 1);
    }
    if (level >= 254) {
        led.plot(2, 0);
    }
}

function plotTemperature(temp: number) {
    led.unplot(0, 0)
    led.unplot(0, 1)
    led.unplot(0, 2)
    led.unplot(0, 3)
    led.unplot(0, 4)
    if (temp >= 10) {
        led.plot(0, 4)
    }
    if (temp >= 20) {
        led.plot(0, 3)
    }
    if (temp >= 30) {
        led.plot(0, 2)
    }
    if (temp >= 40) {
        led.plot(0, 1)
    }
    if (temp >= 50) {
        led.plot(0, 0)
    }
}