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
pass

print("Initializing ServoKit ...")
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
motor_throttle = -1.0

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
    while is_running :
        events = inputs.get_gamepad()
        for e in events:
            code = e.code
            state = e.state
            if code != 'SYN_REPORT' : 
                idx += 1

                print( f"[{idx:04d}] CODE: {e.code}, STATE: {e.state}", end = "" )
                if code == 'ABS_Z' :
                    print( f", servo angle " )
                elif code == 'ABS_Y' :
                    throttle = (127 - state)/127
                    print( f", Throttle = {throttle:.3f}" )
                else :
                    print()
                pass
            pass 
        pass
    pass
pass

print('Press Ctrl+C to quit!')

motor.throttle = -1.0
sleep( 0.1 )

servo_init()
sleep( 1 )
motor_init()

joystick_thread = Thread(target=joystick_control)
joystick_thread.start()

signal.signal(signal.SIGINT, signal_handler)
signal.pause()

joystick_thread.join()

