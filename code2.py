
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
# -----------------------------------------------------------------

""" Global Variables """
programRunning = True

red = DigitalInOut(board.D11)
red.direction = Direction.OUTPUT
red.value = False 

green = DigitalInOut(board.D10)
green.direction = Direction.OUTPUT
green.value = False

blue = DigitalInOut(board.D5)
blue.direction = Direction.OUTPUT
blue.value = False

# this will be the global state for the remote
# handles the logic for what the remote does depending on user interaction
deviceState = 0

#----------------------------------------------------------------------------------
""" Functions """

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
    
    pass


def idle_state():
    # check from inputs from all other states
    # will be polling loop for global vars
    battery_check_state()
    heartbeat(red)
    pass

#IR Reading  function 
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


#Battery check 
def battery_check_state():
    ledBlinkCount = 10 
    battery_voltage_pin = AnalogIn(board.AD0)
    battery_voltage = get_voltage(battery_voltage_pin)
    print(battery_voltage)

    if battery_voltage < 3.4:
        while ledBlinkCount > 10 :
            blue.value = True
            time.sleep(0.25)
            blue.value = False 
            green.value = True
            time.sleep(0.25) 
            green.value = False 
            ledBlinkCount -=1 



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

