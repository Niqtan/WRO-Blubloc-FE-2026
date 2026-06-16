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
eyes = UltrasonicSensor(Port.S3)

hl.set_alg(ALGORITHM_COLOR_RECOGNITION)

DRIVE_SPEED = 600
DODGE_SPEED = 250
LEFT_ANGLE = 70
RIGHT_ANGLE = -30
ADJUST_RIGHT = 5
ADJUST_LEFT = -5
RESET = 0

AREA_THRESHOLD = 55000

def center_wheels():
    steering.run_target(300, 0, then=Stop.HOLD, wait=True)

def get_dist():
    return (eyes.distance() + eyes.distance() + eyes.distance()) / 3

center_wheels()

while True:
    blocks = hl.get_blocks()

    if len(blocks) > 0:
        block = blocks[0]
    #block.ID == 1 is WHITE
        if block.ID == 1:           
            DISTANCE = get_dist()
            AREA_W = block.width * block.height
            print(AREA_W)
            print(DISTANCE)
            print(X)

            print("White mat detected!!")
                 
            # If the area is less than this
            if 60000 <= AREA_W <= 77000 or DISTANCE >= 1000:
                center_wheels()
                drive.run(DRIVE_SPEED)
            elif 200 <= DISTANCE <= 999:
                # This turns left continuously (If the color change to not dominantly white)
                steering.run_target(600, LEFT_ANGLE, Stop.HOLD, wait=True)
                drive.run(DRIVE_SPEED)
        """
        Add:
        Notes:
        - Probably add a sstate machine

        # 159 is neutral; means it realigns
        If x_position == 159:
            steering.run_target(600, 0, Stop.HOLD, wait=True)
            drive.run(DRIVE_SPEED)
        """

         # Filter: Only look at the block if its ID is 2
        if block.ID == 2:
            x_area = block.width * block.height
            if x_area >= 15000:
                # Get the X coordinate of this specific block
                x_position = block.x

                
                print("Found ID 2! X-Coordinate is:", x_position, x_area)
                
                # Example logic: Check if it's on the right side of the screen
                if x_position >= 160:
                    print("ID 2 is on the right side.")
                else:
                    print("ID 2 is on the left side.")
           