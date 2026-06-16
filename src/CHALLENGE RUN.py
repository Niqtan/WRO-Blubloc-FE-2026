from pybricks.hubs import EV3Brick
from pybricks.parameters import Port
from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait
from pyhuskylens import *

ev3 = EV3Brick()

hl = HuskyLens(Port.S1)
steering = Motor(Port.A)
drive = Motor(Port.B)

hl.set_alg(ALGORITHM_COLOR_RECOGNITION)

DRIVE_SPEED = 600
DODGE_SPEED = 250
LEFT_ANGLE = 72
RIGHT_ANGLE = -72
ADJUST_LEFT = 50
ADJUST_RIGHT = -50
RESET = 0

AREA_THRESHOLD = 55000

def center_wheels():
    steering.run_angle(300, 0, then=Stop.HOLD, wait=True)

def get_dist():
    return (eyes.distance() + eyes.distance() + eyes.distance()) / 3

def black_fs():
#block.ID == 2 is BLACK
    if block.ID == 2:
#Assign area to a variable to check if the black area is big enough
        BLACK_AREA = block.width * block.height
        if BLACK_AREA >= 25000:
#Get the x coordinate of said black area (Left, right, middle)
            BLACK_X = block.x
            if BLACK_X > 165:
                print("Black is in the right side")
                steering.run_target(600, ADJUST_LEFT, Stop.HOLD, wait=True)
                drive.run(DRIVE_SPEED)
                wait(150)
                center_wheels()
            elif 155 <=BLACK_X <= 165:
                print("Black is is in middle or is capturing the whole middle")
                steering.run_target(600, LEFT_ANGLE, Stop.HOLD, wait=True)
                drive.run(DRIVE_SPEED)
                wait(150)
                center_wheels()
            else:
                print("Black is in the left side")
                steering.run_target(600, ADJUST_RIGHT, Stop.HOLD, wait=True)
                drive.run(DRIVE_SPEED)
                wait(150)
                center_wheels()
        else:
            print("sensing smalls")
    else:
        print("no black")

#For clarity the RED AND GREEN BLOCKS will now be called MARKERS
#block.ID == 3  is RED (*TRAIN THE HUSKYLENS*)
#block.ID == 4  is GREEN (*TRAIN THE HUSKYLENS*)
def marker_detection(blocks):
    ids = [block.ID for block in blocks]

    BA_RED = 0
    BA_GREEN = 0
    MARKER_TACKLED = None
    SECOND_MARKER = None

    if 3 in ids and 4 in ids:
        print("More than 1 Marker seen")

        for block in blocks:
            if block.ID == 3:
                BA_RED = block.width * block.height
            elif block.ID == 4:
                BA_GREEN = block.width * block.height

        if BA_RED > BA_GREEN:
            MARKER_TACKLED = "RED"
            SECOND_MARKER = "GREEN"

        elif BA_GREEN > BA_RED:
            MARKER_TACKLED = "GREEN"
            SECOND_MARKER = "RED"

    elif 3 in ids:
        MARKER_TACKLED = "AutoRED"

    elif 4 in ids:
        MARKER_TACKLED = "AutoGREEN"

    return MARKER_TACKLED, SECOND_MARKER

#PREMADE SET RUN PATHS needs to be tweaked
def turn_marker(MARKER_TACKLED):

    if MARKER_TACKLED == "AutoRED":
        steering.run_target(600, ADJUST_LEFT, Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(150)
        center_wheels()

    elif MARKER_TACKLED == "AutoGREEN":
        steering.run_target(600, ADJUST_RIGHT, Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(150)
        center_wheels()

    elif MARKER_TACKLED == "GREEN":
        steering.run_target(600, ADJUST_RIGHT, Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(75)

        steering.run_target(600, ADJUST_LEFT, Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(150)

        steering.run_target(600, ADJUST_RIGHT, Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(75)

        center_wheels()

    elif MARKER_TACKLED == "RED":
        steering.run_target(600, ADJUST_LEFT, Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(75)

        steering.run_target(600, ADJUST_RIGHT, Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(150)

        steering.run_target(600, ADJUST_LEFT, Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(75)

        center_wheels()

center_wheels()

#Haven't implemented the MARKER detection and turning yet
#Only implemented the black_fs (black Failsafe)
while True:
    blocks = hl.get_blocks()

    if len(blocks) > 0:
        block = blocks[0]
    #block.ID == 1 is WHITE
        if block.ID == 1:            
            AREA_W = block.width * block.height
            DISTANCE = get_dist()
            print(AREA_W)
            # If the area is between 65000 and 77000
            # Distance greater than 120 (Failsafe)
            # Go Straight
            if 65000 <= AREA_W <= 77000 or DISTANCE >=120:
                center_wheels()
                drive.run(DRIVE_SPEED)
                black_fs(blocks)
            # Turns continously until the area goes back to being between 65000 and 77000
            else:
                # This turns left continuously (If the color change to not dominantly white)
                steering.run_target(600, LEFT_ANGLE, Stop.HOLD, wait=True)
                drive.run(DRIVE_SPEED)

