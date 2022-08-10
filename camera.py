import cv2 as cv
from time import sleep

class Camera :
    def gstream_pipeline(self, camera_id=0, width=1920, height=1080, framerate=10, flip_method=0 ):
        return f"nvarguscamerasrc sensor-id={camera_id} ! video/x-raw(memory:NVMM), width=(int){width}, height=(int){height}, format=(string)NV12, framerate=(fraction){framerate}/1 ! nvvidconv flip-method={flip_method} ! video/x-raw, width=(int){width}, height=(int){height}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True" 

    def __init__(self, size_factor=2) :
        width = 1280//size_factor
        height = 960//size_factor
        GSTREAMER_PIPELINE = self.gstream_pipeline(width=width, height=height) 
        self.cap = cv.VideoCapture(GSTREAMER_PIPELINE, cv.CAP_GSTREAMER)
    pass

    def read(self):
        return self.cap.read()
    pass

    def __del__(self) :
        self.cap.release()
    pass
pass

if __name__ == '__main__':
    """Capture video from camera."""

    print( "Hello .... " )

    camera = Camera()

    for i in range( 40 ) :
        # Capture frame-by-frame
        print( f"{i}", end=",", flush=True )
        ret, frame = camera.read()

        if ret: 
            # Display the resulting frame
            cv.imshow('frame', frame)
            sleep( 0.1 )
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    pass

    # When everything done, release the capture
    cv.destroyAllWindows()

    print( "\nGood bye!" )
pass