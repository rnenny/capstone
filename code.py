import time
import array
import board
import digitalio
from digitalio import DigitalInOut, Direction
from analogio import AnalogIn
import adafruit_matrixkeypad
import adafruit_irremote
import pulseio

# -----------------------------------------------------------------
# State machine using dictionary definitions, as Python does not have switch statements

"""
states:
0 - Idle
1 - Device 1
2 - Device 2
3 - Device 3
4 - Device Programming
"""

# -----------------------------------------------------------------

""" Global Variables """

# state of program
programRunning = True

# this will be the global state for the remote
# handles the logic for what the remote does depending on user interaction
deviceState = 0

# Constant for duty cycle
masterLEDFrequency = 5000
masterLEDDutyCycle = 10000

# LED Vars
red_led_pwm = pulseio.PWMOut(board.D9, frequency=masterLEDFrequency, duty_cycle=0)
green_led_pwm = pulseio.PWMOut(board.D5, frequency=masterLEDFrequency, duty_cycle=0)
blue_led_pwm = pulseio.PWMOut(board.D10, frequency=masterLEDFrequency, duty_cycle=0)

# Status / Heartbeat LED init
status_led = DigitalInOut(board.D13)
status_led.direction = Direction.OUTPUT

# dictionary for keys pressed
key_pressed_dict = {}

# this will be used for storing remote devices when programming
# will hold the header codes and keys programmed (which are the decoded NEC codes)
remote_programming_dict = {}

# I think the diodes are in backwards? (Need verification)
# Swapped rows and columns
# only works when rows and columns are swapped
# I think I just misunderstood what constitutes a row and a column
# Anyways, this works
# Row D6 is now enabled/initialized yet
keypad_rows = [digitalio.DigitalInOut(pin) for pin in (board.A0, board.A1, board.A2, board.A3, board.D6)]
keypad_cols = [digitalio.DigitalInOut(pin) for pin in (board.A4, board.A5)]

keypad_keys = [
    ["power", "volume+", "volume-", "f1", "f3"],
    ["source", "channel+", "channel-", "f2", "f4"],
]

# keypad for universal remote board
remote_keypad = adafruit_matrixkeypad.Matrix_Keypad(keypad_cols, keypad_rows, keypad_keys)

# global bool for if a key is held down
keyPressed = False

# IR setup
ir_pulsein = pulseio.PulseIn(board.D12, maxlen=120, idle_state=True)
ir_decoder = adafruit_irremote.GenericDecode()

ir_transmitter = adafruit_irremote.GenericTransmit((9050, 4460), (550, 1650), (570, 575), 575)
ir_transmitter_pwm = pulseio.PWMOut(board.D11, frequency=30000, duty_cycle=2 ** 14)


# ----------------------------------------------------------------------------------
""" Functions """


def check_keys_pressed():
    global remote_keypad, keyPressed, key_pressed_dict, deviceState

    # this will be a list of returned keys [..., ...]
    keys = remote_keypad.pressed_keys

    # if we have any keys, then loop over the key names
    if keys:
        keyPressed = True

        for key in keys:
            # If-Elseif to handle states for remote
            # force state to idle
            if key == "power":
                deviceState = 0

            # handle reset of deviceState for 'source' key in device_state_3()
            elif key == "source":
                deviceState = 1

            # handle device programming state
            elif key == "f1":
                deviceState = 4

            # update pressed key dictionary
            if key not in key_pressed_dict:
                key_pressed_dict.update({key: 0})
            else:
                key_pressed_dict.update({key: key_pressed_dict.get(key) + 1})

    # wait a bit between key press
    time.sleep(0.015)

    # if no keys, we've released a key
    if len(keys) < 1:
        # only clear key dictionary if there's stuff in there
        if len(key_pressed_dict) > 0:
            key_pressed_dict.clear()

        # set keyPress false because we've released the hold on the key
        keyPressed = False


def test_ir_transmit():
    global ir_transmitter, ir_transmitter_pwm, key_pressed_dict, remote_programming_dict

    # print("Transmitting IR")

    # only process if there are any keys in the dictionary
    if key_pressed_dict:
        # get the all of the keys in the dictionary that are being pressed
        # but from those, only take the first one
        pressed_key = list(key_pressed_dict.keys())[0]

        # proceed if we got a key pressed
        if pressed_key:
            # proceed if we've saved any programmed keys to dictionary
            if remote_programming_dict:
                # if we've saved the key that's being pressed as a programmed key, continue
                if pressed_key in remote_programming_dict:
                    # get the key from the dictionary that has the keys we've programmed
                    programmed_key = remote_programming_dict.get(pressed_key)

                    # create pulse from pwm
                    pulse = pulseio.PulseOut(ir_transmitter_pwm)

                    # get the ir code to transmit from the key we've pressed
                    remote_key_code = programmed_key["code"]

                    # transmit the pulse with the code as the data
                    ir_transmitter.transmit(pulse, array.array('H', remote_key_code))

                    print("Sent Remote IR Code - Key: {}, Code: {}".format(pressed_key, remote_key_code))

    # wait a bit between transmitting
    time.sleep(0.2)


def test_ir_receive():
    global ir_decoder, ir_pulsein, remote_programming_dict

    # read the pulses from the ir receiver; set non-blocking because we're on 1 thread
    pulses = ir_decoder.read_pulses(ir_pulsein, blocking=False)

    # only process if there are any pulses
    if pulses:
        # print("Heard", len(pulses), "Pulses:", pulses)

        try:
            # Attempt to convert received pulses into numbers
            received_code = ir_decoder.decode_bits(pulses)

            # only process if there are any keys in the dictionary
            if key_pressed_dict:
                # get the all of the keys in the dictionary that are being pressed
                # but from those, only take the first one
                pressed_key = list(key_pressed_dict.keys())[0]

                # proceed if we got a key pressed
                if pressed_key:
                    # add the programmed key to the dictionary
                    remote_programming_dict.update({pressed_key: {"code": received_code}})

                    print("Saved - Key: {}, Code: {}".format(pressed_key, received_code))

            # print("NEC Infrared code received: ", received_code)

        except adafruit_irremote.IRNECRepeatException:
            # We got an unusual short code, probably a 'repeat' signal
            print("NEC repeat!")
            return

        except adafruit_irremote.IRDecodeException as e:
            # Something got distorted or maybe its not an NEC-type remote?
            print("Failed to decode: ", e.args)
            return

    # wait a bit between receiving
    time.sleep(0.015)


# function converts value from a pin to a voltage between 0-3.3V
def get_voltage(pin):
    return (pin.value * 3.3) / 65536


def continuous_updates():
    check_keys_pressed()


def battery_check_state():
    global red_led_pwm, green_led_pwm, blue_led_pwm, keypad_rows, masterLEDDutyCycle

    led_blink_count = 0

    # de-init A0 pin from keypad temp
    keypad_rows[0].deinit()
    # give the pin a bit to fully de-initialize
    time.sleep(0.075)

    battery_voltage_pin = AnalogIn(board.A0)
    battery_voltage = get_voltage(battery_voltage_pin) * 2

    print("Battery Voltage: ", battery_voltage)

    # if voltage drops below 5 then blink LEDs 3 times
    if battery_voltage < 5:
        while led_blink_count < 3:
            red_led_pwm.duty_cycle = masterLEDDutyCycle
            time.sleep(0.20)
            red_led_pwm.duty_cycle = 0

            blue_led_pwm.duty_cycle = masterLEDDutyCycle
            time.sleep(0.20)
            blue_led_pwm.duty_cycle = 0

            green_led_pwm.duty_cycle = masterLEDDutyCycle
            time.sleep(0.20)
            green_led_pwm.duty_cycle = 0

            led_blink_count += 1

    # de-init battery_voltage_pin
    battery_voltage_pin.deinit()
    # give the pin a bit to fully de-initialize
    time.sleep(0.075)

    # re-init keyboard pin for key on keypad
    keypad_rows[0] = digitalio.DigitalInOut(board.A0)


def idle_state():
    # check from inputs from all other states
    # will be polling loop for global vars
    battery_check_state()


def device_1_state():
    test_ir_transmit()


def device_2_state():
    global deviceState
    print("device_2_state")
    deviceState = 0


def device_3_state():
    global deviceState
    print("device_3_state")
    deviceState = 0


def device_programming_state():
    test_ir_receive()


# handles state of program and device
# this main loop can return based on the 'deviceState' global variable or either
# in each separate state can set the programRunning variable false to stop the program

while programRunning:
    try:
        # put any code that will run regardless of deviceState in this method
        # KEYBOARD updates
        continuous_updates()

        if deviceState == 0:
            idle_state()

        elif deviceState == 1:
            device_1_state()

        elif deviceState == 2:
            device_2_state()

        elif deviceState == 3:
            device_3_state()

        elif deviceState == 4:
            device_programming_state()

    except KeyboardInterrupt as key_except:
        print(key_except)

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
