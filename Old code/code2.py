import time
import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
import adafruit_matrixkeypad
import adafruit_irremote
import pulseio

# -----------------------------------------------------------------
# State machine using dictonary definitions, as Python does not have switch statements
"""
states:
0 - Idle
1 - Battery CHeck
2 - Device 1
3 - Device 2
4 - Device 3
5 - Device Programming
"""

# -----------------------------------------------------------------

""" Global Variables """
# state of program
programRunning = True

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

# I think the diodes are in backwards? (Need verification)
# Swapped rows and columms
# only works when rows and colums are swapped
# I think I just misunderstood what constitues a row and a column
# Anyways, this works


# this will be the global state for the remote
# handles the logic for what the remote does depending on user interaction
deviceState = 0

# dictionary for keypresses
key_pressed_dict = {}

# Row D6 is now enabled/initialized yet
keypad_rows = [digitalio.DigitalInOut(pin) for pin in (board.A0, board.A1, board.A2, board.A3, board.D6)]
cols = [digitalio.DigitalInOut(pin) for pin in (board.A4, board.A5)]

keys = [
    ["Power", "Volume+", "Volume-", "F1", "F3"],
    ["Source", "Channel+", "Channel-", "F2", "F4"],
]

remote_keypad = adafruit_matrixkeypad.Matrix_Keypad(cols, keypad_rows, keys)
keyPressed = False

# IR setup
pulsein = pulseio.PulseIn(board.D12, maxlen=120, idle_state=True)
decoder = adafruit_irremote.GenericDecode()

# size must match what you are decoding! for NEC use 4
received_code = bytearray(4)

# Docs for adafruit_irremote: (https://circuitpython.readthedocs.io/projects/irremote/en/latest/api.html#implementation-notes)
# Article for IR Apple Remote Code: https://www.hackster.io/BlitzCityDIY/circuit-python-ir-remote-for-apple-tv-e97ea0
# IR Test Code (Apple Remote): https://github.com/BlitzCityDIY/Circuit-Python-Apple-TV-IR-Remote/blob/master/ciruitPython_appleTv_IR-Remote
# pwm out test
OKAY = bytearray(b'\x88\x1e\xc5 ')  # decoded [136, 30, 197, 32]
ir_transmitter = adafruit_irremote.GenericTransmit((9050, 4460), (550, 1650), (570, 575), 575)
ir_transmitter_pwm = pulseio.PWMOut(board.D11, frequency=38000, duty_cycle=2 ** 15)

# ----------------------------------------------------------------------------------
""" Functions """


def check_keypresses():
    global remote_keypad, keyPressed, key_pressed_dict

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


def test_ir_transmit():
    global ir_transmitter, OKAY

    test_pulse = pulseio.PulseOut(ir_transmitter_pwm)
    remote.transmit(test_pulse, OKAY)

    print("Sent Test IR Signal!", OKAY)
    time.sleep(0.2)


def test_ir_receive():
    global decoder, pulsein

    pulses = decoder.read_pulses(pulsein, blocking=False)
    print(pulses)

    if pulses:
        print("Heard", len(pulses), "Pulses:", pulses)

        try:
            # Attempt to convert received pulses into numbers
            received_code = decoder.decode_bits(pulses)
            print("NEC Infrared code received: ", received_code)

        except adafruit_irremote.IRNECRepeatException:
            # We got an unusual short code, probably a 'repeat' signal
            print("NEC repeat!")
            return

        except adafruit_irremote.IRDecodeException as e:
            # Something got distorted or maybe its not an NEC-type remote?
            print("Failed to decode: ", e.args)
            return


def heartbeat(pin):
    while True:
        pin.value = True
        time.sleep(0.5)
        pin.value = False
        time.sleep(0.5)


# function converts value from a pin to a voltage between 0-3.3V
def get_voltage(pin):
    return (pin.value * 3.3) / 65536


def continuous_updates():
    check_keypresses()


# Battery check
def battery_check_state():
    ledBlinkCount = 10
    battery_voltage_pin = AnalogIn(board.AD0)
    battery_voltage = get_voltage(battery_voltage_pin)
    print(battery_voltage)

    if battery_voltage < 3.4:
        while ledBlinkCount > 10:
            blue.value = True
            time.sleep(0.25)
            blue.value = False
            green.value = True
            time.sleep(0.25)
            green.value = False
            ledBlinkCount -= 1


def idle_state():
    # check from inputs from all other states
    # will be polling loop for global vars
    battery_check_state()
    heartbeat(red)
    pass


def device_1_state():
    pass


def device_2_state():
    pass


def device_3_state():
    pass


def device_programming_state():
    pass


# handles state of program and device
# this main loop can return based on the 'deviceState' global variable or either
# in each separate state can set the programRunning variable false to stop the program


while programRunning:

    try:
        # put any code that will run regardless of deviceState in this method
        continuous_updates()

        if deviceState == 0:
            idle_state()

        elif deviceState == 1:
            battery_check_state()

        elif deviceState == 2:
            device_1_state()

        elif deviceState == 3:
            device_2_state()

        elif deviceState == 4:
            device_3_state()

        elif deviceState == 5:
            device_programming_state()

    except KeyboardInterrupt as keyexcept:
        print(keyexcept)

    except() as ex:
        print(ex)

# Status LED setup
# Onboard LED on D13 is always on, and cannot be turned off --
#        This was wrong, we had a bad ground
# However, it may be pulsed using the code below
#        It still can work

# led = DigitalInOut(board.D13)
# led.direction = Direction.OUTPUT
# led.value = False
# while True:
#     led.value = True
#     time.sleep(0.4)
#     led.value = False
#     time.sleep(0.4)
