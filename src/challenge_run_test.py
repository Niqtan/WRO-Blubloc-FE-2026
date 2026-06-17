from pybricks.hubs import EV3Brick
from pybricks.parameters import Port
from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.parameters import Port, Stop
from pybricks.tools import wait
from pyhuskylens import *

ev3 = EV3Brick()

hl = HuskyLens(Port.S1)
eyes = UltrasonicSensor(Port.S3)
steering = Motor(Port.A)
drive = Motor(Port.B)

hl.set_alg(ALGORITHM_COLOR_RECOGNITION)

DRIVE_SPEED = 600
DODGE_SPEED = 250
LEFT_ANGLE = 78
RIGHT_ANGLE = -72
ADJUST_LEFT = 50
ADJUST_RIGHT = -50
RESET = 0

AREA_THRESHOLD = 55000

def center_wheels():
    steering.run_target(300, -2, then=Stop.HOLD, wait=True)

def get_dist():
    return (eyes.distance() + eyes.distance() + eyes.distance()) / 3

"""def black_fs():
#block.ID == 2 is BLACK
    if block.ID == 2:
#Assign area to a variable to check if the black area is big enough
        BLACK_AREA = block.width * block.height
        if BLACK_AREA >= 25000:
#Get the x coordinate of said black area (Left, right, middle)
            BLACK_X = block.x
            if BLACK_X > 165:
                print("Black is in the right side")
                steering.run_target(600, ADJUST_LEFT, then=Stop.HOLD, wait=True)
                drive.run(DRIVE_SPEED)
                wait(150)
                center_wheels()
            elif 155 <=BLACK_X <= 165:
                print("Black is is in middle or is capturing the whole middle")
                steering.run_target(600, LEFT_ANGLE, then=Stop.HOLD, wait=True)
                drive.run(DRIVE_SPEED)
                wait(150)
                center_wheels()
            else:
                print("Black is in the left side")
                steering.run_target(600, ADJUST_RIGHT, then=Stop.HOLD, wait=True)
                drive.run(DRIVE_SPEED)
                wait(150)
                center_wheels()
        else:
            print("sensing smalls")
    else:
        print("no black")"""

#For clarity the RED AND GREEN BLOCKS will now be called MARKERS
#block.ID == 2 is GREEN (*TRAIN THE HUSKYLENS*)
#block.ID == 3  is RED (*TRAIN THE HUSKYLENS*)
def marker_detection(blocks):
    ids = [block.ID for block in blocks]

    BA_RED = 0
    BA_GREEN = 0
    MARKER_TACKLED = None
    SECOND_MARKER = None

    if 2 in ids and 3 in ids:
        print("More than 1 Marker seen")

        for block in blocks:
            if block.ID == 3:
                BA_RED = block.width * block.height
            elif block.ID == 2:
                BA_GREEN = block.width * block.height

        if BA_RED > BA_GREEN:
            MARKER_TACKLED = "RED"
            SECOND_MARKER = "GREEN"

        elif BA_GREEN > BA_RED:
            MARKER_TACKLED = "GREEN"
            SECOND_MARKER = "RED"

    elif 3 in ids:
        MARKER_TACKLED = "AutoRED"

    elif 2 in ids:
        MARKER_TACKLED = "AutoGREEN"

    return MARKER_TACKLED, SECOND_MARKER

#PREMADE SET RUN PATHS needs to be tweaked
def turn_marker(MARKER_TACKLED):

    if MARKER_TACKLED == "AutoRED":
        steering.run_target(600, ADJUST_LEFT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(150)
        center_wheels()

    elif MARKER_TACKLED == "AutoGREEN":
        steering.run_target(600, ADJUST_RIGHT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(150)
        center_wheels()

    elif MARKER_TACKLED == "GREEN":
        steering.run_target(600, ADJUST_RIGHT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        drive.brake()
        wait(75)

        steering.run_target(600, ADJUST_LEFT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        drive.brake()
        wait(150)

        steering.run_target(600, ADJUST_RIGHT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        drive.brake()
        wait(75)

        center_wheels()

    elif MARKER_TACKLED == "RED":
        steering.run_target(600, ADJUST_LEFT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        drive.brake()
        wait(75)

        steering.run_target(600, ADJUST_RIGHT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        drive.brake()
        wait(150)

        steering.run_target(600, ADJUST_LEFT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        drive.brake()
        wait(75)

        center_wheels()

center_wheels()

#Main Execution Loop
# --- Main Execution Loop (Color Recognition Mode) ---
while True:
    blocks = hl.get_blocks()
    DISTANCE = get_dist()

    # 1. Gather all block IDs present in the current camera frame
    ids = [block.ID for block in blocks]
    
    
    """
    this has a bug with the huskylens ai camera because its literally
    detecting the green as 
    """
    white_block = None
    for block in blocks:
        if block.ID == 1:
            white_block = block
            break

    # Ultrasonic failsafe first
    if DISTANCE < 600:
        print("Obstacle physically blocking path! Dodging...")
        steering.run_target(600, LEFT_ANGLE, then=Stop.HOLD, wait=False)
        drive.run(DRIVE_SPEED)
        wait(200)

    elif 2 in ids or 3 in ids:
        marker_to_hit, next_marker = marker_detection(blocks)
        print("Marker triggered:", marker_to_hit)
        turn_marker(marker_to_hit)

    # 4. PRIORITY 3: DEFAULT MASTER STATE (WHITE TRACK LINE KEEPING)
    # If no markers are seen, we force the code to process the white floor template
    elif white_block is not None:
        AREA_W = white_block.width * white_block.height
        print("Defaulting to White Track Layout. Area:", AREA_W)

        # Your original area/distance threshold tracking logic
        if 74000 <= AREA_W <= 77000 or DISTANCE >= 400:
            center_wheels()
            drive.run(DRIVE_SPEED)
        else:
            # If the white area stretches or shifts, make the tracking correction
            steering.run_target(1200, LEFT_ANGLE, then=Stop.HOLD, wait=False)
            wait(200)
            drive.run(DRIVE_SPEED)

    # 5. FALLBACK CATCH-ALL
    else:
        # If the screen goes totally black, green-glitched, or blank
        print("Lost all reliable color tracking IDs! Coasting on default...")
        center_wheels()
        drive.run(DRIVE_SPEED)

    wait(100)