from adafruit_servokit import ServoKit
import board, busio, numpy as np
from time import sleep

print( "Disconnect the Motor cabel from the power!" )
text = input ( "Enter to continue! " )

print("Initializing ServoKit ...")
i2c = busio.I2C(board.SCL, board.SDA)
kit = ServoKit(channels=16, i2c=i2c)
print("Done initializing servokit.")

motor = kit.continuous_servo[ 1 ]

print( "" )
motor.throttle = 1.0
sleep( 1 )

print( "Connect the Motor cable to the power! " )
input( "Enter to continue ..." )
print( "Wait for 5 seconds! " )
sleep( 5 )

motor.throttle = 0
sleep( 1 )

print( "Good bye!" )
