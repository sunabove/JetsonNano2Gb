from adafruit_servokit import ServoKit
import board, busio, numpy as np
from time import sleep

print("Initializing ServoKit ...")
kit = ServoKit(channels=16, i2c=busio.I2C(board.SCL, board.SDA))
print("Done initializing servokit.")

servo = kit.continuous_servo[ 0 ]

servo.throttle = -1.0
sleep( 1 )

duration = 0.2

for throttle in np.arange( -1, 1, 0.01 ) :
    print( f"servo throttle = {throttle:.2f}", flush=True )
    servo.throttle = throttle
    sleep( duration )

for throttle in np.arange( 1, -1, -0.01 ) :
    print( f"servo throttle = {throttle:.2f}", flush=True )
    servo.throttle = throttle
    sleep( duration ) 

print( "Good bye!" )