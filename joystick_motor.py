from operator import is_
import inputs, signal, sys
import board, busio, numpy as np
from time import sleep
from threading import Thread 
from adafruit_servokit import ServoKit

is_running = True

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    print( "Move joystick to quit!")
    global is_running
    is_running = False
    sleep( 1 )
    motor.throttle = -1.0
    sys.exit( 0 )
pass

print("Initializing ServoKit .... ")
kit = ServoKit(channels=16, i2c=busio.I2C(board.SCL, board.SDA))
print("Done initializing servokit.")

servo = kit.servo[0]
motor = kit.continuous_servo[ 1 ]

servo_duration = 0.015
motor_duration = 0.5

min_angle = 45 
max_angle = 115
cen_angle = int( (max_angle + min_angle)/2 )

servo_angle = cen_angle
throttle_inc_ratio = 0
max_throttle = 0.30
min_throttle = -0.30

def servo_init() :
    print( "Initializing servo angles ..." )
    angles_group = [ ]
    angles_group.append( np.arange( cen_angle, max_angle + 1, 1 ) )
    angles_group.append( np.arange( max_angle, min_angle - 1, -1 ) )
    angles_group.append( np.arange( min_angle, cen_angle + 1, 1 ) )

    prev_text = None
    print( f"Servo: angle = ", end="" )
    
    duration = servo_duration
    for angles in angles_group:
        for angle in angles : 
            if prev_text is not None :
                back_len = len( prev_text )
                print( back_len*"\b", end="" )
                print( back_len*" ", end="" )
                print( back_len*"\b", end="" )

            prev_text = f"{angle}"
            print( f"{angle}", flush=True, end="" )
            servo.angle = angle 
            sleep( duration )
        pass
        sleep( 0.5 )
    pass
    print() 
    print( "Done. initializing servo angles!" )
pass

def motor_init() :
    print( "Initializing motor throttle ..." )
    motor.throttle = -1.0
    sleep( 0.1 )

    duration = 0.5

    min_throttle = - 0.2
    max_throttle = - 0.1

    throttles_group = []
    throttles_group.append( np.arange( min_throttle, max_throttle, + 0.01 ) )
    throttles_group.append( np.arange( max_throttle, min_throttle, - 0.01 ) )

    print( f"throttle = ", end="" )
    prev_text = None
    for throttles in throttles_group : 
        for throttle in throttles :
            if prev_text is not None :
                back_len = len( prev_text )
                print( back_len*"\b", end="" )
                print( back_len*" ", end="" )
                print( back_len*"\b", end="" )
            prev_text = f"{throttle:.2f}"
            print( prev_text, flush=True, end="" )
            motor.throttle = throttle
            sleep( duration )
        pass
        sleep( 1 )
    pass

    motor.throttle = -1.0
    sleep( 0.1 )

    print()
    print( "Done initializing motor throttle!" )
pass

def joystick_control() :
    if len(inputs.devices.gamepads) < 1 :
        raise Exception("Couldn't find any Gamepads!")
    else :
        print( "Gamepads found." )
    pass

    print( "Power on the joystick and press any key!" )
    idx = 0 
    global is_running, servo_angle, throttle_inc_ratio

    while is_running :
        events = inputs.get_gamepad()
        for e in events:
            code = e.code
            state = e.state
            if code != 'SYN_REPORT' : 
                idx += 1

                print( f"[{idx:04d}] CODE: {e.code}, STATE: {e.state}", end = "" )
                if code in ( 'ABS_Z', 'ABS_X' ) :
                    global min_angle, max_angle, servo_angle
                    angle = (max_angle - min_angle)*(255- state)/255 + min_angle
                    angle = int( angle )
                    servo_angle = angle
                    print( f", servo angle = {servo_angle}" )
                elif code == 'ABS_Y' :
                    throttle_inc_ratio = (127-state)/127
                    print( f", throttle_inc_ratio = {throttle_inc_ratio:.3f}, throttle = {motor.throttle:.3f}" )
                elif code in ( 'BTN_SELECT' , 'BTN_MODE', 'BTN_START' ) :
                    is_running = False 
                else :
                    print()
                pass
            pass 
        pass
    pass
pass

def servo_control() :
    global is_running

    duration = servo_duration
    while is_running :
        diff = servo_angle - servo.angle 
        if abs( diff ) <= 1 :
            sleep( 2*duration ) 
        else :
            angle = servo.angle + 1.0*np.sign( diff )
            angle = angle%360
            angle = min( 180, max( 0, angle ) )
            #print( f"angle = {angle}, increment = {diff}" )
            servo.angle = angle
            sleep( duration )
        pass 
    pass
pass

def motor_control() :
    global is_running

    duration = 0.1
    while is_running :
        if abs( throttle_inc_ratio ) < 0.001 :
            sleep( 2*duration ) 
        else :
            throttle = motor.throttle + 0.05*np.sign( throttle_inc_ratio )
            #throttle = max( min_throttle, min( max_throttle , throttle ) )
            throttle = max( -1.0, min( 1.0 , throttle ) )
            motor.throttle = throttle

            print( f"throttle = {throttle:.3f}, throttle_inc_ratio = {throttle_inc_ratio:.3f}" )
            sleep( duration )
        pass 
    pass
pass

print('Press Ctrl+C to quit!')

motor.throttle = -1.0
sleep( 0.1 )

do_init = False 
if do_init:
    servo_init()
    sleep( 1 )
    motor_init()
pass

threads = []

joystick_thread = Thread(target=joystick_control)
servo_thread = Thread(target=servo_control)
motor_thread = Thread(target=motor_control)

threads.append( joystick_thread )
threads.append( servo_thread )
threads.append( motor_thread )

for thread in threads :
    thread.start()
pass


signal.signal(signal.SIGINT, signal_handler)
signal.pause()

for thread in threads :
    thread.join()
pass

print( "Good bye!" )
