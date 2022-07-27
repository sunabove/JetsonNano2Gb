from adafruit_servokit import ServoKit
import board, busio, numpy as np
from time import sleep

print("Initializing ServoKit ...")
kit = ServoKit(channels=16, i2c=busio.I2C(board.SCL, board.SDA))
print("Done initializing servokit.")

motor = kit.continuous_servo[ 1 ]

motor.throttle = -1.0
sleep( 1 )

for throttle in np.arange( -0.5, 0.5, 0.1 ) :
    print( f"throttle = {throttle:.2f}", flush=True )
    motor.throttle = throttle
    sleep( 1 )

motor.throttle = -1.0

sleep( 2 )

print( "Good bye!" )