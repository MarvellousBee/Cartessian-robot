from machine import Pin
import time


STOPPER_BUTTON_Y = Pin(14, Pin.IN, Pin.PULL_UP)
STOPPER_BUTTON_Z = Pin(15, Pin.IN, Pin.PULL_UP)
STOPPER_BUTTON_X1 = Pin(16, Pin.IN, Pin.PULL_UP)
STOPPER_BUTTON_X2 = Pin(17, Pin.IN, Pin.PULL_UP)

#2345
motor_pins = {"x1":[2,4,3,5],
          "z":[10,12,11,13],
           "y":[6,8,7,9],
        "x2":[18,20,19,21],
        "g":[0,1]
          }

motor_final = {}

"""
base = [2,4,3,5] # 2 i 3 odwrócone
m1 = [10,12,11,13] # 10 i 11 odwrócone
m2 = [6,8,7,9] # 6 i 7 odwrócone
"""

for motor_name, pins in motor_pins.items():
    for i in range(len(pins)):
        motor_pins[motor_name][i] = Pin(pins[i], Pin.OUT)

Steps = [
    "1000",
    "1100",
    "0100",
    "0110",
    "0010",
    "0011",
    "0001",
    "1001",
    ]

current_steps = {}
current_delay_steps = {}
current_position = {}


for a,b in motor_pins.items():
    current_steps[a] = 0
    current_delay_steps[a] = 0
    current_position[a] = 0

base_current_delay_steps = current_delay_steps

def step(what, dir):
    #what - motor name
    #dir  - direction (1 or -1)
    global current_steps, current_position

    current_position[what]+=dir

    if what=="g":

        if dir==1:
            motor_pins[what][0].value(1)
            motor_pins[what][1].value(0)
        else:
            motor_pins[what][0].value(0)
            motor_pins[what][1].value(1)

        return

    for i in range(4):
        motor_pins[what][i].value(int(Steps[current_steps[what]][i]))

    current_steps[what] = (current_steps[what]+dir)%8

def move(orders): #1 milisecond minimum delay
    global current_delay_steps, current_position

    #micropython deepcopy()
    dupa = {}
    for mtr, ords in orders.items():
        dupa[mtr] = ords[:]

    #main loop
    while dupa:
        for motor, order in dupa.items():
            if current_delay_steps[motor]==0:
                step(motor, order[1])
                dupa[motor][0]-=1

                if len(dupa[motor])==4:#endstop button
                    if not dupa[motor][3].value():
                        del dupa[motor]
                        current_position[motor]=0


                elif dupa[motor][0] == 0:
                    if motor=="g":
                        motor_pins[motor][0].value(0)
                        motor_pins[motor][1].value(0)
                    del dupa[motor]

            current_delay_steps[motor] = (current_delay_steps[motor]+1)%order[2]
        time.sleep(.001)

    #reset delays
    current_delay_steps = base_current_delay_steps


#which motor, direction, delay, limit switch





#Do not exceed
max_pos = {"x1":999999999,
           "x2":999999999,
           "y": 999999999,
           "z": 999999999,
           }


def auto_home(speed):
    #home y
    move({"y": [99999,1,speed, STOPPER_BUTTON_Y]})
    print("y done")
    #home z
    move({"z": [99999,-1,speed, STOPPER_BUTTON_Z]})
    print("z done")
    #home x
    move({"x1":[99999,-1,speed, STOPPER_BUTTON_X1],
         "x2":[99999,-1,speed, STOPPER_BUTTON_X2]})
    print("x done")


try:
    auto_home(5)
    """
    move({"g":[3,1,300]})
    move({"x1":[2000,1,3],
         "x2":[2000,1,3],
         "z":[2000,-1,3],
         "y":[2000,1,3]})
    """




except KeyboardInterrupt:
    GPIO.cleanup()
