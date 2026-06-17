from pybricks.hubs import EV3Brick
from pybricks.parameters import Port, Stop
from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.tools import wait
from pyhuskylens import *

ev3 = EV3Brick()

hl = HuskyLens(Port.S1)
eyes = UltrasonicSensor(Port.S3)
steering = Motor(Port.A)
drive = Motor(Port.B)

# --- CHANGED TO LINE TRACKING ALGORITHM ---
hl.set_alg(ALGORITHM_LINE_TRACKING)

DRIVE_SPEED = 600
DODGE_SPEED = 250
LEFT_ANGLE = 78
RIGHT_ANGLE = -72
ADJUST_LEFT = 50
ADJUST_RIGHT = -50
RESET = 0

def center_wheels():
    # Only command the motor if it is physically drifted out of center bounds
    if steering.angle() < -6 or steering.angle() > 2:
        steering.run_target(300, -2, then=Stop.HOLD, wait=True)

def get_dist():
    return (eyes.distance() + eyes.distance() + eyes.distance()) / 3

# For clarity the RED AND GREEN BLOCKS will now be called MARKERS
# (Maintained for reference or multi-line configurations if needed)
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

# PREMADE SET RUN PATHS
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
        wait(75)

        steering.run_target(600, ADJUST_LEFT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(150)

        steering.run_target(600, ADJUST_RIGHT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(75)
        center_wheels()

    elif MARKER_TACKLED == "RED":
        steering.run_target(600, ADJUST_LEFT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(75)

        steering.run_target(600, ADJUST_RIGHT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(150)

        steering.run_target(600, ADJUST_LEFT, then=Stop.HOLD, wait=True)
        drive.run(DRIVE_SPEED)
        wait(75)
        center_wheels()

# Initial initialization
center_wheels()

# --- Main Execution Loop ---
while True:
    # Read the distance to any hurdle obstacles directly in front
    DISTANCE = get_dist()
    
    # 1. PRIORITY 1: OBSTACLE BYPASS (Using Ultrasonic Failsafe)
    if DISTANCE < 600:
        print("Obstacle detected via Ultrasonic! Executing bypass...")
        # Automatically dodges left to clear a standard layout obstacle hurdle
        turn_marker("AutoRED") 
        
    # 2. PRIORITY 2: LINE KEEPING AND STEERING
    else:
        # Request lines from the HuskyLens
        lines = hl.get_arrows()

        if len(lines) > 0:
            for line in lines:
                # ID == 1 is your main learned line track
                if line.ID == 1:
                    x_target = line.x_head
                    print("Line Target X:", x_target, "Distance:", DISTANCE)

                    # PATH CONDITION A: Track is straight ahead (Dead center is 160)
                    if 140 <= x_target <= 180:
                        center_wheels()
                        drive.run(DRIVE_SPEED)
                    
                    # PATH CONDITION B: Track is breaking away to the Left
                    elif x_target < 140:
                        steering.run_target(1200, LEFT_ANGLE, then=Stop.HOLD, wait=False)
                        drive.run(DRIVE_SPEED)
                        
                    # PATH CONDITION C: Track is breaking away to the Right
                    elif x_target > 180:
                        steering.run_target(1200, RIGHT_ANGLE, then=Stop.HOLD, wait=False)
                        drive.run(DRIVE_SPEED)
        else:
            # If the line drops entirely due to extreme glare, hold path safely
            print("No line seen. Coasting forward...")
            drive.run(DRIVE_SPEED)

    # Throttled loop to 15ms so the data streaming matches the camera refresh rate
    wait(15)