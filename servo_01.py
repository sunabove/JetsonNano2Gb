from time import sleep
from adafruit_servokit import ServoKit

print( "Hello..." )
kit = ServoKit(channels=16)
    
for servo_pin in range( 0, 1 ) :
    print( f"servo_pin = {servo_pin}", flush=True )    
    kit.servo[servo_pin].angle=0
    sleep( 0.5 )
    kit.servo[servo_pin].angle=45
    sleep( 0.5 )
    kit.servo[servo_pin].angle=90
    sleep( 0.5 )
pass
print( "Good bye!" )