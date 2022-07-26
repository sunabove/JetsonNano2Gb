from time import sleep
from adafruit_servokit import ServoKit

print( "Hello..." )
kit = ServoKit(channels=16)
    
for servo_pin in range( 0, 16 ) :
    print( f"servo_pin = {servo_pin}" )
    kit.servo[servo_pin].angle=90
    sleep( 1 )
    kit.servo[servo_pin].angle=120
    sleep( 1 )
    kit.servo[servo_pin].angle=150
    sleep( 1 )
pass
print( "Good bye!" )