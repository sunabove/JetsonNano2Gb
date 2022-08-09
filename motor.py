from adafruit_servokit import ServoKit
import board, busio, numpy as np
from time import sleep

print("Initializing ServoKit ...")
i2c = busio.I2C(board.SCL, board.SDA)
kit = ServoKit(channels=16, i2c=i2c)
print("Done initializing servokit.")

motor = kit.continuous_servo[ 1 ]

max_throttle =  0.4 
min_throttle = -0.4

motor.throttle = 0.0
sleep( 1 )

duration = 0.2
print( "Forward ....")
for throttle in np.arange( 0, max_throttle, 0.01 ) :
    print( f"throttle = {throttle:.2f}", flush=True )
    motor.throttle = throttle
    sleep( duration )

print( "\nDecresing speed ...")
for throttle in np.arange( max_throttle, 0, -0.01 ) :
    print( f"throttle = {throttle:.2f}", flush=True )
    motor.throttle = throttle
    sleep( duration ) 

print( "\nBackward ....")
motor.throttle = -1.0
sleep( 1 )
for throttle in np.arange( 0, min_throttle, -0.01 ) :
    print( f"throttle = {throttle:.2f}", flush=True )
    motor.throttle = throttle
    sleep( duration ) 

motor.throttle = 0.0
sleep( 1 )

print( "\nGood bye!" )
