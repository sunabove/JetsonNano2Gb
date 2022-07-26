from time import sleep
from adafruit_servokit import ServoKit
import board, busio
import numpy as np

print( "Hello ..." )

print("Initializing ServoKit")
kit = ServoKit(channels=16, i2c=busio.I2C(board.SCL, board.SDA))
print("Done initializing")

print( "Ready to move ..." ) 

servo = kit.servo[1]

duration = 0.2

min_angle = 45 
max_angle = 140

for angle in range( min_angle, max_angle, 1 ) : 
    print( f"servo: angle = {angle}", flush=True )
    servo.angle = angle
    sleep( duration )
pass

for angle in range( max_angle, min_angle, -1 ) : 
    print( f"servo: angle = {angle}", flush=True )
    servo.angle = angle
    sleep( duration )
pass

servo.angle = 0
sleep( 2 )

print( "Good bye!" )