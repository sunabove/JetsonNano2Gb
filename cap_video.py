# cap_video.py
import cv2 as cv
from time import sleep
def gstream_pipeline( camera_id, capture_width=1920, capture_height=1080,
        display_width=1920, display_height=1080, framerate=30, flip_method=0 ):
    return (
            "nvarguscamerasrc sensor-id=%d ! video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"
            % ( camera_id, capture_width, capture_height, framerate, flip_method, display_width, display_height )   )

cap = cv.VideoCapture( gstream_pipeline(camera_id=0, capture_width=640, capture_height=480, display_width=640, display_height=480), cv.CAP_GSTREAMER)
for i in range( 100 ) :
    ret, frame = cap.read()
    cv.imshow('frame', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):  break
cap.release()
cv.destroyAllWindows()