#coding: utf-8

import sys, numpy as np, threading, logging as log, inspect, signal
import cv2 as cv, psutil

from time import time, sleep
from flask import Flask, render_template, Response, request, jsonify

log.basicConfig(
    format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)04d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S', level=log.INFO
    )

app = None

def gstream_pipeline(
        camera_id=0, width=1920, height=1080, framerate=10, flip_method=0 ):
    return f"nvarguscamerasrc sensor-id={camera_id} ! video/x-raw(memory:NVMM), width=(int){width}, height=(int){height}, format=(string)NV12, framerate=(fraction){framerate}/1 ! nvvidconv flip-method={flip_method} ! video/x-raw, width=(int){width}, height=(int){height}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"  

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

    text = f"FRM NO: {frame_cnt}/{frame_no}, Ratio = { (frame_cnt/frame_no)*100:3.1f} %" 
    tx = 10
    ty = 20
    th = 20   # line height
    fg_color = (0, 255, 0) 
    bg_color = (50, 50, 60)
    putTextLine( image, text, tx, ty, fg_color, bg_color )

    text = ""
    pct = psutil.virtual_memory()[2]  # RAM 사용량 출력 
    text += f"MEM : {pct:02.1f} %"
    
    pct = psutil.cpu_percent() # CPU 사용량 출력 
    text += f" CPU : {pct:03.1f} %"

    ty += th
    fg_color = (0, 0, 255) if pct >= 90 else (0, 255, 0)
    bg_color = (50, 50, 60)
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

def stop():
    global app, camera, is_running
    
    print( "", flush=True) 

    log.info( 'VCar stopping ...' ) 

    is_running = False

    if camera is not None :
        camera.release()
    pass

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
        
        return render_template('index_robot_server.html', **config )
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

        if cmd == "stop" :
            pass
        elif cmd == "forward":
            pass
        elif cmd == "backward":
            pass
        elif cmd == "turn_left":
            pass
        elif cmd == "turn_right":
            pass
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