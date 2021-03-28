let response = ""
let microbitDevices: string[] = []
let sensorValues: string[] = []
let state = 0
// 0: idle, 1: handshaking, 2: listening to serial, 3: cmd received, wrtie to serial 
let commandStartTime = 0
let handshakeStartTime = 0
let buffer: string[] = []
handshakeStartTime = 0
commandStartTime = 0
radio.setGroup(0)
radio.setTransmitSerialNumber(true)
radio.setTransmitPower(7)

serial.onDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    const data = serial.readLine()
    if (data.includes("handshake")) {
        if (state == 0) {
            state = 1
            radio.sendString(data)
            handshakeStartTime = input.runningTime()
        }
    } else if (data.includes('poll')) {
        if (state == 2) {
            state = 3
            commandStartTime = input.runningTime()
            sensorValues = []
            radio.sendString(data)
        }
    } else if (data.includes('fire') || data.includes('reset')) {
        radio.sendString(data)
    }
})
radio.onReceivedString(function (receivedString) {
    if (receivedString.includes('enrol=')) {
        if (state == 1) {
            buffer = receivedString.split('=')
            microbitDevices.push(buffer[1])
        }
    } else if (receivedString.includes('-')) {
        if (state == 3) {
            sensorValues.push(receivedString)
        }
    }
})

input.onButtonPressed(Button.A, function () {
    serial.writeLine("abcd")
})

basic.forever(function () {
    basic.showNumber(state)
    if (state == 1) {
        if (input.runningTime() - handshakeStartTime > 5 * 1000) {
            state = 2
            response = ""
            for (let microbitDevice of microbitDevices) {
                if (response.length > 0) {
                    response = "" + response + "," + microbitDevice
                } else {
                    response = microbitDevice
                }
            }
            serial.writeLine("enrol=" + response)
        }
    } else if (state == 3) {
        if (input.runningTime() - commandStartTime > 5 * 1000) {
            response = ""
            for (let sensorValue of sensorValues) {
                if (response.length > 0) {
                    response = "" + response + "," + sensorValue
                } else {
                    response = sensorValue
                }
            }
            serial.writeLine("" + response)
            state = 2
        }
    }
})
