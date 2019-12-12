# The MIT License (MIT)
#
# Copyright (c) 2017 Scott Shawcroft for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#adafruit_irremote
====================================================

import time
import board
import pulseio
import digitalio
from digitalio import DigitalInOut, Direction, Pull
import adafruit_irremote
import adafruit_matrixkeypad

# --------------------------------------------------------------------
# RGB LED code section. See schematic for pin usage
# Red - D9
# Green - D10
# Blue - D5
# NEEDED TO INITILIZED PIN VALUES OR WONKY STUFF HAPPENS
# CircuitPython takes care of active low pins interanally?
# In this case False = False, as it would on active high pins


red = DigitalInOut(board.D9)
red.direction = Direction.OUTPUT
red.value = False

green = DigitalInOut(board.D10)
green.direction = Direction.OUTPUT
green.value = False

blue = DigitalInOut(board.D5)
blue.direction = Direction.OUTPUT
blue.value = False

# Status / Heartbeat LED init
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
# led.value = True
# --------------------------------------------------------------------
# Init IR recievers
# ir_recieve1 = DigitalInOut(board.D12)
# ir_recieve1.direction = Direction.INPUT
#ir_recieve1.value = 0

#ir_recieve2 = DigitalInOut(board.D13)
#ir_recieve2.direction =  Direction.INPUT
#ir_recieve2.value = 0

# --------------------------------------------------------------------
# mfet = DigitalInOut(board.D11)
# mfet.direction = Direction.OUTPUT
# mfet.value = 1


#I think the diodes are in backwards? (Need verification)
# Swapped rows and columms
# only works when rows and colums are swapped
# I think I just misunderstood what constitues a row and a column
# Anyways, this works 

key_dict = {}

# Row D6 is now enabled/initialized yet
rows = [digitalio.DigitalInOut(x) for x in (board.A0, board.A1, board.A2, board.A3, board.D6)]
cols = [digitalio.DigitalInOut(x) for x in (board.A4, board.A5)]

keys = [
    ["Power", "Volume+", "Volume-", "F1", "F3"],
    ["Source", "Channel+", "Channel-", "F2",  "F4"],
]


keypad = adafruit_matrixkeypad.Matrix_Keypad(cols, rows, keys)
keyPressed = False

# IR setup
pulsein = pulseio.PulseIn(board.D12, maxlen=120, idle_state=True)
decoder = adafruit_irremote.GenericDecode()
received_code = bytearray(4) # size must match what you are decoding! for NEC use 4

# Docs for adafruit_irremote: (https://circuitpython.readthedocs.io/projects/irremote/en/latest/api.html#implementation-notes)
# Article for IR Apple Remote Code: https://www.hackster.io/BlitzCityDIY/circuit-python-ir-remote-for-apple-tv-e97ea0
# IR Test Code (Apple Remote): https://github.com/BlitzCityDIY/Circuit-Python-Apple-TV-IR-Remote/blob/master/ciruitPython_appleTv_IR-Remote
# pwm out test
OKAY = bytearray(b'\x88\x1e\xc5 ') #decoded [136, 30, 197, 32]
remote = adafruit_irremote.GenericTransmit((9050, 4460), (550, 1650), (570, 575), 575)
pwm = pulseio.PWMOut(D11, frequency = 38000, duty_cycle = 2 ** 15)

while True:
    # Blink LED
    led.value = True
    time.sleep(0.2)
    led.value = False
    time.sleep(0.2)


    """ Test IR Transmit """
    # test_pulse = pulseio.PulseOut(pwm)
    # remote.transmit(test_pulse, OKAY)
    # print("Sent Test IR Signal!", OKAY)
    # time.sleep(0.2)



    """ Test IR Readings """
    # pulses = decoder.read_pulses(pulsein, blocking=False)
    # print(pulses)

    # if pulses:
    #     print("Heard", len(pulses), "Pulses:", pulses)
        
    #     try:
    #         # Attempt to convert received pulses into numbers
    #         received_code = decoder.decode_bits(pulses)
    #         print("NEC Infrared code received: ", received_code)

    #     except adafruit_irremote.IRNECRepeatException:
    #         # We got an unusual short code, probably a 'repeat' signal
    #         print("NEC repeat!")
    #         continue
    #     except adafruit_irremote.IRDecodeException as e:
    #         # Something got distorted or maybe its not an NEC-type remote?
    #         print("Failed to decode: ", e.args)
    #         continue
 

    # this will be a list of returned keys'; [..., ...]
    keys = keypad.pressed_keys

    # if we have any keys, then loop over the key names
    if keys:
        keyPressed = True

        for key in keys:
            if key not in key_dict:
                key_dict.update({key: 0})
            else:
                key_dict.update({key: key_dict.get(key) + 1})

        print(key_dict)
        # print("Pressed: ", keys)

    time.sleep(0.015)

    if len(keys) < 1:
        if len(key_dict) > 0:
            key_dict.clear()
        keyPressed = False


print("Got here because exception or end of program")