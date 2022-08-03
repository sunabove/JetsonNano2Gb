import cv2 as cv, time, threading, psutil
from flask import Response, Flask

global video_frame
video_frame = None

global thread_lock 
thread_lock = threading.Lock() 

def gstream_pipeline(
        camera_id=0, width=1920, height=1080, framerate=10, flip_method=0 ):
    return f"nvarguscamerasrc sensor-id={camera_id} ! video/x-raw(memory:NVMM), width=(int){width}, height=(int){height}, format=(string)NV12, framerate=(fraction){framerate}/1 ! nvvidconv flip-method={flip_method} ! video/x-raw, width=(int){width}, height=(int){height}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"  

size_factor = 4
GSTREAMER_PIPELINE = gstream_pipeline(width=1280//size_factor, height=960//size_factor) 
cap = cv.VideoCapture(GSTREAMER_PIPELINE, cv.CAP_GSTREAMER)

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
    global frame_cnt

    text = f"Frame: {frame_cnt:04d}" 
    tx = 10
    ty = 20
    th = 20   # line height
    fg_color = (0, 255, 0) 
    bg_color = (50, 50, 60)
    putTextLine( image, text, tx, ty, fg_color, bg_color )

    # CPU 사용량 출력
    pct = psutil.cpu_percent()
    text = f"CPU : {pct:02.1f} %"
    ty += th
    fg_color = (0, 0, 255) if pct >= 90 else (0, 255, 0)
    bg_color = (50, 50, 60)
    putTextLine( image, text, tx, ty, fg_color, bg_color )

    # RAM 사용량 출력
    pct = psutil.virtual_memory()[2]
    ty += th
    fg_color = (0, 0, 255) if pct >= 90 else (0, 255, 0)
    bg_color = (50, 50, 60)
    text = f"RAM : {pct:02.1f} %"
    putTextLine( image, text, tx, ty, fg_color, bg_color )

    frame_cnt += 1
    return image
pass

app = Flask(__name__)

def capture_frames():
    global video_frame, thread_lock

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret :
            break

        with thread_lock:            
            video_frame = frame.copy()
            vidoe_frame = process_image( video_frame )
        pass
    pass
pass

def encode_frame():
    global thread_lock
    while True:
        # Acquire thread_lock to access the global video_frame object
        with thread_lock:
            global video_frame
            if video_frame is None:
                continue

            ret, encoded_image = cv.imencode(".jpg", video_frame)
            
            if not ret:
                continue
            pass
        pass

        # Output image as a byte array
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encoded_image) + b'\r\n')
        pass
    pass
pass

@app.route("/")
def stream_frames():
    return Response(encode_frame(), mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
    capture_thread = threading.Thread(target=capture_frames)
    capture_thread.daemon = True
    capture_thread.start()

    try : 
        app.run("0.0.0.0", port="8080")
    finally:
        print( "Shutting down now ..." )
        print( "Camera is closing now... ", flush=True )
        cap.release()
        print( "Good bye!", flush=True )
    pass
pass