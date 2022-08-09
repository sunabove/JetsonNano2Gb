from adafruit_servokit import ServoKit
import board, busio, numpy as np
from time import sleep

print( "Hello ..." )

print("Initializing ServoKit ...")
i2c = busio.I2C(board.SCL, board.SDA)
kit = ServoKit(channels=16, i2c=i2c)
print("Done initializing servokit.")

servo = kit.servo[0]

duration = 0.2

min_angle = 45 
max_angle = 115
cen_angle = int( (max_angle + min_angle)/2 )

# turn to the left
for angle in range( cen_angle, max_angle + 1, 1 ) : 
    print( f"servo: angle = {angle}", flush=True )
    servo.angle = angle
    sleep( duration )
pass

# turn to the right
for angle in range( max_angle, min_angle -1, -1 ) : 
    print( f"servo: angle = {angle}", flush=True )
    servo.angle = angle
    sleep( duration )
pass

# turn to the center
for angle in range( min_angle, cen_angle + 1, 1 ) : 
    print( f"servo: angle = {angle}", flush=True )
    servo.angle = angle
    sleep( duration )
pass

print( "Good bye!" )