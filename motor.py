from time import sleep
from adafruit_servokit import ServoKit
import board, busio, numpy as np

print( "Hello ..." )
#kit = ServoKit(channels=16, address=0x40)
kit = ServoKit(channels=16, i2c=busio.I2C(board.SCL, board.SDA))

print( "Ready to move ..." )

throttle_motor = kit.continuous_servo[ 0 ]

motor = throttle_motor
motor.throttle = -1.0 
sleep( 1 )

for throttle in np.arange( -0.5, 0.5, 0.1 ) :
    print( f"throttle = {throttle}", flush=True )
    motor.throttle = throttle
    sleep( 1 )

motor.throttle = -1.0

sleep( 2 )

print( "Good bye!" )