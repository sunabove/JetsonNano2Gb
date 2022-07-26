import inputs, signal, sys, threading
import board, busio, numpy as np
from time import sleep 
from adafruit_servokit import ServoKit

is_running = True

print("Initializing ServoKit .... ")
i2c = busio.I2C(board.SCL, board.SDA)
kit = ServoKit(channels=16, i2c=i2c)
print("Done initializing servokit.")

servo = kit.servo[0]
motor = kit.continuous_servo[ 1 ]

servo_duration = 0.015
motor_duration = 0.5

min_angle = 45 
max_angle = 115
cen_angle = int( (max_angle + min_angle)/2 )
servo_angle = cen_angle

throttle_max  = 1.0
throttle_zero = -0.15
throttle_min  = -1.0
throttle_to   = throttle_zero 

servo_thread = None
motor_thread = None 

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
    throttle_init_max = -0.15

    throttles_group = []
    throttles_group.append( np.arange( throttle_zero, throttle_init_max, 0.01 ) )
    throttles_group.append( np.arange( throttle_init_max, throttle_zero, - 0.01 ) ) 

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
        sleep( 3 )
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
    global is_running, throttle_to
    global min_angle, max_angle, servo_angle
    global servo_thread, motor_thread
    
    duration = 0.1
    while is_running :
        events = inputs.get_gamepad()
        for e in events:
            code = e.code
            state = e.state
            if code not in ( 'SYN_REPORT' ) :  
                idx += 1

                print( f"[{idx:04d}] CODE: {e.code}, STATE: {e.state}", end = "" )
                if code in ( 'ABS_Z', 'ABS_X' ) :
                    # servo control
                    angle = (max_angle - min_angle)*(255- state)/255 + min_angle
                    angle = int( angle )
                    servo_angle = angle
                    print( f", servo angle = {servo_angle}", flush=True )

                    if servo_thread is None :
                        servo_thread = threading.Thread(target=servo_control, daemon=True)
                        servo_thread.start()
                    pass
                elif code == 'ABS_Y' :
                    # motor control
                    throttle_ratio = (127 - state)/127
                    if throttle_ratio > 0 :
                        throttle_to = abs(throttle_max - throttle_zero)*throttle_ratio + throttle_zero
                    else :
                        throttle_to = abs(throttle_zero - throttle_min)*throttle_ratio + throttle_zero
                    pass

                    throttle_to = max( throttle_min, min( throttle_max, throttle_to) )
                    throttle_to = max( -1.0, min( 1.0, throttle_to) )

                    print( f", throttle_ratio = {throttle_ratio:.3f}, throttle_to = {throttle_to:.3f} throttle_curr = {motor.throttle:.3f}", flush=True )

                    if motor_thread is None :
                        motor_thread = threading.Thread(target=motor_control, daemon=True)
                        motor_thread.start()
                    pass
                else :
                    print()
                pass
            pass 
            sleep( duration )
        pass
    pass
pass

def servo_control() :
    global is_running, servo_thread

    duration = servo_duration
    while is_running :
        diff = servo_angle - servo.angle 
        
        if abs( diff ) <= 1 :
            servo_thread = None
            break
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

def set_throttle( throttle_to ) : 
    while True :
        diff = throttle_to - motor.throttle
        inc = diff if abs( diff ) < 0.1 else diff/3.0
        print( f"curr throttle = {motor.throttle:.4f}, to throttle = {throttle_to}, inc = {inc:.4f}" )
        
        if -1.0 <= ( motor.throttle + inc ) <= 1.0 :
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

def motor_control() :
    duration = 0.1
    global is_running, motor_thread, throttle_to
    
    while is_running  :
        if throttle_to < 0 and motor.throttle > 0 :
            motor.throttle = -1.0
            sleep( duration )
        pass

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
            motor_thread = None
            break
        pass 
    pass
pass

print('Press Ctrl+C to quit!')

motor.throttle = throttle_zero
sleep( 0.2 )

do_init = False 
if do_init:
    servo_init()
    sleep( 1 )
    motor_init()
    print()
pass

try :
    joystick_control()
finally:
    is_running = False

    motor.throttle = throttle_zero
    sleep( 1 )
pass

if servo_thread is not None :
    servo_thread.join()
pass

if motor_thread is not None :
    motor_thread.join()
pass

print( "Good bye!" )
