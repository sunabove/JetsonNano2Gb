from time import sleep
from adafruit_servokit import ServoKit

print( "Hello..." )
kit = ServoKit(channels=16, address=0x40)

print( "Ready to move" )

steering_motor = kit.continuous_servo[ 0 ]
throttle_motor = kit.continuous_servo[ 1 ]

steering_motor.throttle = 1
throttle_motor.throttle = 1

sleep( 2 )

print( "Good bye!" )