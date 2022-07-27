# SDA = pin.SDA_1
# SCL = pin.SCL_1
# SDA_1 = pin.SDA
# SCL_1 = pin.SCL

from adafruit_servokit import ServoKit
import board, busio
from time import sleep

# On the Jetson Nano
# Bus 0 (pins 28,27) is board SCL_1, SDA_1 in the jetson board definition file
# Bus 1 (pins 5, 3) is board SCL, SDA in the jetson definition file
# Default is to Bus 1; We are using Bus 0, so we need to construct the busio first ...
do_servo_test = False 
if do_servo_test : 
    print("Initializing ServoKit ...")
    kit = ServoKit(channels=16, i2c=busio.I2C(board.SCL, board.SDA))
    # kit[0] is the bottom servo
    # kit[1] is the top servo
    print("Done initializing.")

    servo = kit.servo[0]

    duration = 0.2

    for degree in range(0, 180) :
        servo.angle=degree
        # kit.servo[1].angle=degree
        sleep( duration )

    sleep(0.5) 

    for degree in range(180, 0, -1) :
        servo.angle = degree
        sleep( duration )
    pass

    print( "Done moving servo.")
pass

print( "Joystick ...." )
from approxeng.input.selectbinder import ControllerResource

last_presses = None

with ControllerResource() as joystick:
    print(type(joystick).__name__)
    while joystick.connected:
        axis_list = [ 'lx', 'ry' ]
        for axis_name in axis_list:
            # desired_angle is in degrees
            joystick_value = joystick[axis_name]
            # The joystick value goes from -1.0 ... 1.0 (a range of 2)
            # Normalize within a range of 180 degrees
            desired_angle = (joystick_value+1)/2*180
            
            if  axis_name == 'lx' :
                kit.servo[0].angle=desired_angle
                # print(axis_name, joystick[axis_name])
                
            if axis_name == 'ry' :
                    kit.continuous_servo[1].throttle=joystick[axis_name]
    
