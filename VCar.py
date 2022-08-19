import os, sys, numpy as np, threading, logging as log, inspect, signal
import cv2 as cv, psutil

from time import time, sleep
from flask import Flask, render_template, Response, request, jsonify

log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

app = None

########## Camera #####################
def gstream_pipeline( camera_id=0, width=1920, height=1080, framerate=10, flip_method=0 ):
    return f"nvarguscamerasrc sensor-id={camera_id} ! video/x-raw(memory:NVMM), width={width}, height={height}, format=NV12, framerate=(fraction){framerate}/1 ! nvvidconv flip-method={flip_method} ! video/x-raw, width={width}, height={height}, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink max-buffers=1 drop=True"  

size_factor = 2
GSTREAMER_PIPELINE = gstream_pipeline(width=1280//size_factor, height=960//size_factor) 
camera = cv.VideoCapture(GSTREAMER_PIPELINE, cv.CAP_GSTREAMER)

is_running = True
video_frame = None
frame_no = 0 
capture_thread = None

def putTextLine(image, txt, x, y, fg_color=None, bg_color=None, font_size=0.4 ) :
    # opencv 이미지에 텍스트를 그린다.
    font = cv.FONT_HERSHEY_SIMPLEX
    fs = font_size  # font size(scale)
    ft = 1    # font thickness 

    if fg_color is None : 
        fg_color = (255, 0, 0) # text foreground color
    
    if bg_color is None :
        bg_color = (255, 255, 255) # text background color

    if image is not None and len( image.shape ) == 2 : #gray scale
        bg_color = (255, 255, 255) # white
        fg_color = (0, 0, 0)  # black
    pass

    cv.putText(image, txt, (x, y), font, fs, bg_color, ft + 2, cv.LINE_AA)
    cv.putText(image, txt, (x, y), font, fs, fg_color, ft    , cv.LINE_AA) 
pass # -- putTextLine

frame_cnt = 0 
def process_image( image ) :
    global frame_cnt, frame_no

    tx = 10
    ty = 0
    th = 20   # line height
    fg_color = (0, 255, 0)
    bg_color = (255, 255, 255)
    
    texts = []
    
    throttle = motor.throttle
    throttle_rel = throttle - throttle_zero
    angle = servo.angle
    angle_rel = angle - angle_cen

    text = f"Throt : max {throttle_max:.2f} zero {throttle_zero:.2f} min {throttle_min:.2f}"    
    text += f" abs {throttle:.2f} rel {throttle_rel:.2f}"
    texts.append( text )
    
    text = f"Angle : max {angle_max:.1f} cen {angle_cen:.1f} min {angle_min:.1f}"
    text += f" abs {angle:.1f} rel {angle_rel:.1f}"
    texts.append( text )

    text = f"FRM NO: {frame_cnt}/{frame_no}, Ratio = { (frame_cnt/frame_no)*100:3.1f} %" 
    texts.append( text )

    for text in texts :
        ty += th
        putTextLine( image, text, tx, ty, fg_color, bg_color )
    pass

    ram_usage = psutil.virtual_memory()[2]  # RAM 사용량 출력 
    cpu_usage = psutil.cpu_percent() # CPU 사용량 출력 
    text = f"MEM : {ram_usage:02.1f} % CPU : {cpu_usage:03.1f} %"

    ty += th
    fg_color = (0, 0, 255) if cpu_usage >= 90 else (0, 255, 0)
    putTextLine( image, text, tx, ty, fg_color, bg_color )

    frame_cnt += 1

    return image
pass

def capture_frames():
    global is_running, video_frame, frame_no

    while is_running and camera.isOpened():
        ret, frame = camera.read()
        if not ret :
            break

        video_frame = frame
        frame_no += 1
    pass
pass

def encode_frame():
    global is_running, video_frame, frame_no
    curr_frame_no = frame_no -1

    while is_running :
        if ( video_frame is not None ) and ( curr_frame_no < frame_no ):
            curr_frame_no = frame_no

            frame = process_image( video_frame )
            ret, encoded_image = cv.imencode(".jpg", frame)
        
            if not ret:
                continue
            pass 

            # Output image as a byte array
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encoded_image) + b'\r\n')
        else : 
            sleep( 0.1 )
        pass
    pass
pass

########### SERVO/MOTOR ####################
print("Initializing ServoKit .... ")
import board, busio
from adafruit_servokit import ServoKit

i2c = busio.I2C(board.SCL, board.SDA)
kit = ServoKit(channels=16, i2c=i2c)
print("Done initializing servokit.")

servo = kit.servo[0]
motor = kit.continuous_servo[ 1 ]

servo_duration = 0.015
motor_duration = 0.1

angle_min = 45 
angle_max = 115
angle_cen = int( (angle_min + angle_max)/2 )

throttle_max  = 0.3
throttle_zero = -0.15
throttle_min  = - throttle_max
throttle_to   = throttle_zero 

throttle_req_no = 0 
servo_req_no = 0 

def set_throttle( throttle_to ) : 
    global motor, throttle_req_no

    throttle_req_no += 1
    
    curr_req_no = throttle_req_no

    duration = motor_duration
    throttle_to = min( throttle_max, max( throttle_min, throttle_to ) )
    throttle_to = min( 1.0, max( -1.0, throttle_to ) )

    while curr_req_no == throttle_req_no :
        if throttle_to < 0 and motor.throttle >= 0 :
            motor.throttle = -1.0
            sleep( duration )
        pass

        diff = throttle_to - motor.throttle

        inc = diff if abs( diff ) < 0.1 else diff/3.0
        print( f"curr throttle = {motor.throttle:.4f}, to throttle = {throttle_to}, inc = {inc:.4f}" )
        
        if abs( diff ) < 0.1 :
            motor.throttle = throttle_to
        elif throttle_min <= ( motor.throttle + inc ) <= throttle_max :
            motor.throttle += inc
        else :
            motor.throttle = throttle_to
        pass

        sleep( duration )

        if abs( diff ) < 0.1 :
            break
        pass
    pass
pass

def set_steering( angle_to ) :
    global servo, servo_req_no

    servo_req_no += 1

    curr_req_no = servo_req_no
    
    duration = servo_duration

    angle_to = min( angle_max, max( angle_min, angle_to ) )
    angle_to = min( 180, max( 0, angle_to ) )
        
    while curr_req_no == servo_req_no :
        diff = angle_to - servo.angle
        inc = diff if abs( diff ) < 2.0 else ( 2.0*np.sign( diff ) )

        print( f"curr angle = {servo.angle:.4f}, to angle = {angle_to}, inc = {inc:.4f}" )

        if abs( diff ) < 2.0 :
            servo.angle = angle_to
        elif angle_min <= ( servo.angle + inc ) <= angle_max :
            servo.angle += inc
        else :
            servo.angle = angle_to
        pass

        sleep( duration )

        if abs( diff ) < 2.0 :
            break
        pass
    pass
pass

##### MOTOR INITIALIZE
print( "Motor initializing ...") 
set_throttle( throttle_zero )
print( "Done. Motor initializaing.")

##### SERVO INITIALIZE
print( "Servo initializing ...")
set_steering( angle_cen )
print( "Done. Servo initializaing." )

def stop():
    global app, camera, is_running
    
    print( "", flush=True) 

    log.info( 'VCar stopping ...' ) 

    is_running = False

    if camera is not None :
        camera.release()
    pass

    set_throttle( throttle_zero )
    set_steering( angle_cen )

    if app is not None : 
        app.do_teardown_appcontext()
    pass

    log.info( "Good bye!" )
pass # -- stop

def start() : 
    global app, capture_thread, is_running

    is_running = True

    log.info( "Hello....." )

    # web by flask framewwork

    app = Flask(__name__, static_url_path='', static_folder='html', template_folder='html')
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    
    @app.before_request
    def before_request_func():
        global capture_thread

        if capture_thread is None : 
            capture_thread = threading.Thread(target=capture_frames)
            capture_thread.daemon = True
            capture_thread.start()
        pass
    pass

    @app.route( '/' )
    @app.route( '/index.html' )
    @app.route( '/index.htm' )
    def index(): 
        config = {}
        
        return render_template('index_vcar.html', **config )
    pass 

    @app.route('/video')
    def video(): 
        return Response(encode_frame(), mimetype = "multipart/x-mixed-replace; boundary=frame") 
    pass 

    @app.route("/cmd", methods=['POST'] )
    def process_cmd():
        global motor, servo
        
        cmd = request.form.get("cmd")
        val = request.form.get("val")

        log.info(f"cmd={cmd}, val={val}")

        if cmd == "shutdown":
            result = os.popen("sync && sync && sudo shutdown now").read().strip()
            print( f"Result = {result}")
        elif cmd == "stop" :
            set_throttle( throttle_zero ) 
        elif cmd == "forward":
            throttle_to = motor.throttle + abs(throttle_max - throttle_zero)/10.0
            set_throttle( throttle_to )
        elif cmd == "backward":
            throttle_to = motor.throttle - abs(throttle_zero - throttle_min)/5.0
            set_throttle( throttle_to )
        elif cmd == "turn_left":
            set_steering( servo.angle + (angle_max - angle_min)/10.0 )
        elif cmd == "turn_right":
            set_steering( servo.angle - (angle_max - angle_min)/10.0 )
        pass

        return "OK"
    pass

    log.info( "## Normal WEB")

    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True) 

    log.info( "Good bye!")
pass # -- service

if __name__=='__main__':
    if 'stop' in sys.argv :
        stop()
    else :
        def signal_handler(signal, frame):
            print()
            print( '\nYou have pressed Ctrl-C.' ) 

            stop() 

            sleep( 2 )

            sys.exit(0)
        pass

        signal.signal(signal.SIGINT, signal_handler)

        start()
    pass
pass
