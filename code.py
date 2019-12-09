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

green =DigitalInOut(board.D10)
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
#Init IR recievers 
ir_recieve1 = DigitalInOut(board.D12)
ir_recieve1.value = 0
ir_recieve2 = DigitalInOut(board.D13)
ir_recieve2.value = 0

# --------------------------------------------------------------------
mfet = DigitalInOut(board.D11)
mfet.value = 1 



cols = [digitalio.DigitalInOut(x) for x in (board.A4, board.A5)]
rows = [digitalio.DigitalInOut(x) for x in (board.A0, board.A1)]

key_dict = {}
keys = [
    ["Power", "Volume+"],
    ["Source", "Channel+"]
]

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
keyPressed = False

while True:
    # Blink LED
    led.value = True
    time.sleep(0.2)
    led.value = False
    time.sleep(0.2)

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

# pulsein = pulseio.PulseIn(board.D13, maxlen=120, idle_state=True)
# decoder = adafruit_irremote.GenericDecode()
#
# # size must match what you are decoding! for NEC use 4
# received_code = bytearray(4)
#
# while True:
#     pulses = decoder.read_pulses(pulsein)
#     print("Heard", len(pulses), "Pulses:", pulses)
#     try:
#         code = decoder.decode_bits(pulses)
#         print("Decoded:", code)
#     except adafruit_irremote.IRNECRepeatException:  # unusual short code!
#         print("NEC repeat!")
#     except adafruit_irremote.IRDecodeException as e:     # failed to decode
#         print("Failed to decode: ", e.args)