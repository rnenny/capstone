import time
import board
import pulseio
import digitalio
from digitalio import DigitalInOut, Direction, Pull
import adafruit_irremote
import adafruit_matrixkeypad

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

cols = [digitalio.DigitalInOut(x) for x in (board.A0, board.A1)]
rows = [digitalio.DigitalInOut(x) for x in (board.A4, board.A5)]

key_dict = {}
keys = [
    ["Power", "Volume+"],
    ["Source", "Channel+"]
]

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
keyPressed = False

while True:
    # Blink LED
    # led.value = True
    # time.sleep(0.2)
    # led.value = False
    # time.sleep(0.2)

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