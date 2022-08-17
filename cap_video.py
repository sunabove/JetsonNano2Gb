# cap_video.py
import cv2 as cv
from time import sleep

def gstream_pipeline(
        camera_id=0, width=1920, height=1080, framerate=10, flip_method=0 ):
    return f"nvarguscamerasrc sensor-id={camera_id} ! video/x-raw(memory:NVMM), width={width}, height={height}, format=NV12, framerate=(fraction){framerate}/1 ! nvvidconv flip-method={flip_method} ! video/x-raw, width={width}, height={height}, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink max-buffers=1 drop=True"  

size_factor = 2
GSTREAMER_PIPELINE = gstream_pipeline(width=1280//size_factor, height=960//size_factor) 
camera = cv.VideoCapture(GSTREAMER_PIPELINE, cv.CAP_GSTREAMER)

for i in range( 100 ) :
    ret, frame = camera.read()
    cv.imshow('frame', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
    pass
pass

camera.release()
cv.destroyAllWindows()