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
sideeyes = UltrasonicSensor(Port.S4)

hl.set_alg(ALGORITHM_COLOR_RECOGNITION)

STEER_SPEED = 600
DRIVE_SPEED = 450
BACK_SPEED = -600


#Values for avoiding blocks
RIGHT_ANGLE = -75
LEFT_ANGLE = 75

#Base turning angle(Value to be changed if clockwise or counter)
ANGLE = 80

"""
Clockwise / counter clockwise logic
#Value either -1 or 1 to be multiplied to ANGLE for counter or clockwise
"""
TRACK_DIRECTION = 0 
CORRECTION = 15

#Counter
COUNT = 0

#Distance 1 or distance two to be used in fuction dist():
D_ONE = 0
D_TWO = 0
D_C = 0

def center_wheels():
    steering.run_target(1000, 0, then=Stop.HOLD, wait=True)

def dist():
    return (eyes.distance() + eyes.distance() + eyes.distance()) / 3

def side_dist():
    return (sideeyes.distance() + sideeyes.distance() + sideeyes.distance()) / 3

def get_dist_OPEN():
    global TRACK_DIRECTION, ANGLE, D_ONE, D_TWO

    #Takes two distances
    #One from start (Base distance from wall)
    D_ONE = side_dist()
    drive.dc(100)
    wait(1000)
    drive.stop()
    #One after it moved forward (Sees if the distance from wall moved or change)
    D_TWO = side_dist()
    wait(500)
    #Takes difference
    print(D_ONE)
    print(D_TWO)
    """ changed: d2 - d1 -> D_TWO - D_ONE """
    DIFF = abs(D_TWO - D_ONE)
    #From 1-99 keeps it as clockwise(Incase the robot it turning to either left or right slightly)
    if DIFF <= 999:
        print("Clockwise")
        TRACK_DIRECTION = 1
        ANGLE = TRACK_DIRECTION * 60
    #From 100 upwards changes to counter-clockwise meaning massive distance change and so it's facing the open area ie facing other way
    elif DIFF >= 1000:
        print("Counterclockwise")
        TRACK_DIRECTION = -1
        ANGLE = TRACK_DIRECTION * 60

def get_dist_CHALLENGE():

    global TRACK_DIRECTION, ANGLE

    D_C = side_dist()
    if D_C >= 250:
        print("Counterclockwise")
        TRACK_DIRECTION = 1
        ANGLE = TRACK_DIRECTION * 60
    elif D_C <= 249:
        print("Clockwise")
        TRACK_DIRECTION = -1
        ANGLE = TRACK_DIRECTION * 60

def exit_parking():
    DIR_LEFT = TRACK_DIRECTION * LEFT_ANGLE
    DIR_RIGHT = TRACK_DIRECTION * RIGHT_ANGLE
    while dist() < 160:
        drive.run(-200)

    # Turn left because we're exiting left out
    steering.run_target(1000, DIR_LEFT, then=Stop.HOLD, wait=False)
    drive.dc(60)
    wait(950)
    drive.brake()

    center_wheels()
    # Turn right to turn the right way
    steering.run_target(1000, DIR_RIGHT, then=Stop.HOLD, wait=False)
    drive.dc(-60)
    wait(950)
    drive.brake()

    # Turn left because we're exiting left out
    steering.run_target(1000, DIR_LEFT, then=Stop.HOLD, wait=False)
    wait(1500)
    drive.dc(60)
    wait(2000)
    drive.brake()
    # Turn right to turn the right way 
    steering.run_target(1000, DIR_RIGHT, then=Stop.HOLD, wait=False)
    drive.dc(80)
    wait(800)
    steering.run_target(1000, DIR_LEFT, then=Stop.HOLD, wait=False)   
    drive.dc(-80)
    wait(1000)
    steering.run_target(1000, DIR_RIGHT, then=Stop.HOLD, wait=False)
    drive.dc(80)
    wait(800)
    drive.brake()

def marker_detection(blocks):
    print("Detecting block")

    MARKER_TACKLED = "None"
    TARGET_AREA = 0

    totoong_bricks = []

    for block in blocks:
        if block.ID in [2,3]:

            """Changed: block.height / block.width -> block.width / block.height"""
            aspect_ratio = block.width / block.height
            print("ID:", block.ID, "Ratio:", aspect_ratio)
            if aspect_ratio <= 1.2: # Lower the number to be more strict on the lines if needed
                totoong_bricks.append(block)

    totoong_ids = [b.ID for b in totoong_bricks]

    if 3 in totoong_ids and not 2 in totoong_ids:
        MARKER_TACKLED = "AutoRED"
        for block in blocks:
            if block.ID == 3: 
                TARGET_AREA = block.width * block.height

    elif 2 in totoong_ids and not 3 in totoong_ids:
        MARKER_TACKLED = "AutoGREEN"
        for block in blocks:
            if block.ID == 2: 
                TARGET_AREA = block.width * block.height

    return MARKER_TACKLED, TARGET_AREA

def turn_marker(MARKER_TACKLED):
    DIR_LEFT = TRACK_DIRECTION * LEFT_ANGLE
    DIR_RIGHT = TRACK_DIRECTION * RIGHT_ANGLE

    if MARKER_TACKLED == "AutoRED":
        #Start turning
        steering.run_target(1000, DIR_RIGHT, then=Stop.HOLD, wait=True)
        #Takes target Area, while target area is still seen...KEEP TURNING
        while True:
            blocks = hl.get_blocks()
            TARGET_AREA = 0

            for block in blocks:
                if block.ID == 3:  # RED marker
                    TARGET_AREA = block.width * block.height

            if TARGET_AREA == 0:
                break
        #Stop once it's not seen.
        wait(400)
        #TO BE CONTINUED (TURN BACK TO FACE OTHER BLOCK...)
        steering.run_target(1000, DIR_LEFT, then=Stop.HOLD, wait=False)
        wait(1250)
        center_wheels()

        drive.hold()

    elif MARKER_TACKLED == "AutoGREEN":
        #Start turning
        steering.run_target(1000, DIR_LEFT, then=Stop.HOLD, wait=True)
        #Takes target Area, while target area is still seen...KEEP TURNING
        while True:
            blocks = hl.get_blocks()
            TARGET_AREA = 0

            for block in blocks:
                if block.ID == 2:  # GREEN marker
                    TARGET_AREA = block.width * block.height

            if TARGET_AREA == 0:
                break
        #Stop once it's not seen.
        wait(400)
        #TO BE CONTINUED (TURN BACK TO FACE OTHER BLOCK...)
        steering.run_target(1000, DIR_RIGHT, then=Stop.HOLD, wait=False)
        wait(1250)
        center_wheels()

        drive.hold()
def counter():
    global COUNT
    COUNT += 1
    return COUNT

# Figure out direction first
get_dist_CHALLENGE()
# Now exit parallel parking
exit_parking()
#wait and check if there's a block in front of it
wait(500)
while True:
    blocks = hl.get_blocks()

    if len(blocks) > 0:
        block = blocks[0]
    #block.ID == 1 is WHITE
        if block.ID == 1:            
            AREA_W = block.width * block.height
            # If the area is between this and dist() >=1000
            # Run straight forward
            if 65000 <= AREA_W <= 77000 and dist() >= 1000:
                center_wheels()
                drive.run(DRIVE_SPEED)
                if 1900 >= side_dist() >= 400 :
                    print(side_dist())
                    steering.run_angle(STEER_SPEED, -CORRECTION, then=Stop.HOLD, wait=True)
                    wait(250) # keep corrections brief
                    center_wheels()
                elif side_dist() < 400:
                    print(side_dist())
                    steering.run_angle(STEER_SPEED, CORRECTION, then=Stop.HOLD, wait=True)
                    wait(250)
                    center_wheels()
            # If the area is less than 65000 or greater than 77000 then you do normal turn
            # The cause of turn is because the white area got disturbed
            elif 65000 > AREA_W or AREA_W > 77000:
                ANGLE = TRACK_DIRECTION*80
            # This turns left continuously (If the color change to not dominantly white)
                steering.run_target(1000, ANGLE, then=Stop.HOLD, wait=True)
                # IDEA: We can realign straight by moving backward onto the wall to straighten ourselves.
                drive.stop()
            # If the distance is less than 1000 (need calibrating) theen you run the color_mark code
            # The cause is because the distance sensor sensed a block 
            elif dist() < 1000:
                wait(2000)
                color_mark, area_block = marker_detection(blocks)                    
                if color_mark != "None" and area_block >= 3000:
                    turn_marker(color_mark)
                else:
                    break

        else:
            # Failsafe when the camera goes temporarily blind
            # Just makes it crawl
            drive.run(DRIVE_SPEED // 2)


