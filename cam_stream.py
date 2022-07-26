import cv2, time, threading
from flask import Response, Flask

global video_frame
video_frame = None

global thread_lock 
thread_lock = threading.Lock() 

def gstream_pipeline(
        camera_id=0, capture_width=1920, capture_height=1080,
        display_width=1920, display_height=1080, framerate=30, flip_method=0, ):
    return (
            "nvarguscamerasrc sensor-id=%d ! video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"
            % ( camera_id, capture_width, capture_height,
                    framerate, flip_method,
                    display_width, display_height,
            )
    )

app = Flask(__name__)
GSTREAMER_PIPELINE = gstream_pipeline(capture_width=640, capture_height=480, display_width=640, display_height=480) 
GSTREAMER_PIPELINE = gstream_pipeline(capture_width=960, capture_height=720, display_width=960, display_height=720) 
video_capture = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)

def capture_frames():
    global video_frame, thread_lock

    while video_capture.isOpened():
        return_key, frame = video_capture.read()
        if not return_key:
            break

        with thread_lock:
            video_frame = frame.copy()

def encode_frame():
    global thread_lock
    while True:
        # Acquire thread_lock to access the global video_frame object
        with thread_lock:
            global video_frame
            if video_frame is None:
                continue
            return_key, encoded_image = cv2.imencode(".jpg", video_frame)
            if not return_key:
                continue

        # Output image as a byte array
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encoded_image) + b'\r\n')

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
        video_capture.release()
        print( "Good bye!", flush=True )
    pass
pass