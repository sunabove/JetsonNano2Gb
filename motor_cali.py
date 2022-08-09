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

motor.throttle = 0.0
sleep( 0.1 )

def set_throttle( throttle_to) : 
    while True :
        diff = throttle_to - motor.throttle
        inc = diff if abs( diff ) < 0.1 else diff/3.0
        print( f"curr throttle = {motor.throttle:.4f}, to throttle = {throttle_to}, inc = {inc:.4f}" )
        
        if -1.0 <= motor.throttle <= 1.0 :
            motor.throttle += inc
        else :
            motor.throttle = throttle_to
        pass

        sleep( 0.1 )

        if abs( diff ) < 0.1 :
            break
        pass
    pass
pass

print( "Sending maximum throttle signal ...." )
set_throttle( 1.0 )
sleep( 1 )

print( "\nConnect the Motor cable to the power! " )
input( "Enter to continue ..." )
print( "Wait for 5 seconds! " )
sleep( 5 )

print( "Sending minimum throttle signal ...." )
set_throttle( 0.0 )
sleep( 5 )

print( "Good bye!" )
