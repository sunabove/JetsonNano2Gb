from time import sleep
from adafruit_servokit import ServoKit
import numpy as np

print( "Hello ..." )
kit = ServoKit(channels=16, address=0x40)

print( "Ready to move ..." )

throttle_motor = kit.continuous_servo[ 0 ]
steering_motor = kit.continuous_servo[ 1 ]

motor = throttle_motor
for throttle in np.arange( -0.5, 0.5, 0.1 ) :
    print( f"throttle = {throttle}", flush=True )
    motor.throttle = throttle
    sleep( 1 )

motor.throttle = -1.0 

#throttle_motor.throttle = 1

sleep( 2 )

print( "Good bye!" )