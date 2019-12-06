# Write your code here :-)
# CircuitPython IO demo #1 - General Purpose I/O
import time
import board
from digitalio import DigitalInOut, Direction, Pull
import digitalio
from analogio import AnalogIn
import adafruit_matrixkeypad



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

""" Global Variables """
programRunning = True

# this will be the global state for the remote
# handles the logic for what the remote does depending on user interaction

deviceState = 0

# LED light
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

""" Functions """


# function converts value from a pin to a voltage between 0-3.3V
def get_voltage(pin):
    return (pin.value * 3.3) / 65536


def continuous_updates():
    pass


def idle_state():
    # check from inputs from all other states
    # will be polling loop for global vars
    pass

def test_ir_reading():
    pulsein = pulseio.PulseIn(board.REMOTEIN, maxlen=120, idle_state=True)
    decoder = adafruit_irremote.GenericDecode()

    # size must match what you are decoding! for NEC use 4
    received_code = bytearray(4)

    while True:
        # this array will contain tuples ex. (data, data, etc...)
        saved_data = []

        pulses = decoder.read_pulses(pulsein)
        print("Heard", len(pulses), "Pulses:", pulses)
        
        try:
            code = decoder.decode_bits(pulses)

            # save current pulse and decoded bits to array
            data_tuple = (pulses, code)

            saved_data.append(data_tuple)

            # pulses, code = saved_data[0]


            print("Decoded:", code)
            
        except adafruit_irremote.IRNECRepeatException:  # unusual short code!
            print("NEC repeat!")
        except adafruit_irremote.IRDecodeException as e:  # failed to decode
            print("Failed to decode: ", e.args)

def battery_check_state():
    battery_voltage_pin = AnalogIn(board.AD0)
    battery_voltage = get_voltage(battery_voltage_pin)
    print(battery_voltage)

    if battery_voltage < 2.2:
        ledBlinkCount = 10
        while ledBlinkCount > 0:
            led.value = True
            time.sleep(0.015)
            led.value = False
            ledBlinkCount -= 1

    count = 10
    while count > 0:
        print(battery_voltage_pin.value)
        count -= 1
        time.sleep(0.1)


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
# Onboard LED on D13 is always on, and cannot be turned off
# However, it may be pulsed using the code below

# led = DigitalInOut(board.D13)
# led.direction = Direction.OUTPUT
# led.value = False
# while True:
#     led.value = True
#     time.sleep(0.4)
#     led.value = False
#     time.sleep(0.4)


# --------------------------------------------------------------------
# RGB LED code section. See schematic for pin usage

# red = DigitalInOut(board.D11)
# red.direction = Direction.OUTPUT

# green =DigitalInOut(board.DXX)
# green.direction = Direction.OUTPUT

# blue = DigitalInOut(board.DXX)
# blue.direction = Direction.OUTPUT


# -----------------------------------------------------------------------
# while True:
#     led.value = True
#     time.sleep(0.4)

#     led.value = False
#     time.sleep(0.4)

#     print(red.value)
#     red.value = 1
#     #time.sleep(0.4)
#     #red.value = 0


# --------------------------------------------------------------------------------------
# Keyboard matrix setup

# cols = [digitalio.DigitalInOut(x) for x in (board.D4, board.D5)]  # Columns with corresponding pins, in digital mode
# rows = [digitalio.DigitalInOut(x) for x in
#         (board.D0, board.D1, board.D4, board.D6)]  # Rows with corresponding pins in digital modes
# keys = (('Power', 'Source'),  # Set up up as seen in remote diagram
#         ('Volume+', 'VChannel+')
#         ('Volume-', 'Channel-')
#         ('F1', 'F2')
#         ('F3', 'F4'))
