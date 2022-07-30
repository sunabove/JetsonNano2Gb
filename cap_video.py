"""Capture video from camera."""
import cv2 as cv
from time import sleep

print( "Hello .... " )

def gstream_pipeline( camera_id=0, width=1920, height=1080, framerate=10, flip_method=0 ):
    return f"nvarguscamerasrc sensor-id={camera_id} ! video/x-raw(memory:NVMM), width=(int){width}, height=(int){height}, format=(string)NV12, framerate=(fraction){framerate}/1 ! nvvidconv flip-method={flip_method} ! video/x-raw, width=(int){width}, height=(int){height}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True" 
   
cap = cv.VideoCapture( gstream_pipeline( width=640, height=480), cv.CAP_GSTREAMER)

#cap = cv.VideoCapture(0)
#cap.set(cv.CAP_PROP_FPS, 10)

for i in range( 20 ) :
    # Capture frame-by-frame
    print( f"{i}", end=",", flush=True )
    ret, frame = cap.read()

    if ret: 
        # Display the resulting frame
        cv.imshow('frame', frame)
    #sleep( 0.01 )
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()

print( "Good bye!" )
