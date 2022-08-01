import numpy as np, cv2 as cv
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('*.jpg')

def gstream_pipeline(
        camera_id=0, width=1920, height=1080, framerate=10, flip_method=0 ):
    return f"nvarguscamerasrc sensor-id={camera_id} ! video/x-raw(memory:NVMM), width=(int){width}, height=(int){height}, format=(string)NV12, framerate=(fraction){framerate}/1 ! nvvidconv flip-method={flip_method} ! video/x-raw, width=(int){width}, height=(int){height}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"  

size_factor = 4
GSTREAMER_PIPELINE = gstream_pipeline(width=1280//size_factor, height=960//size_factor) 
cap = cv.VideoCapture(GSTREAMER_PIPELINE, cv.CAP_GSTREAMER)

while cap.isOpened() :
    ret, img = cap.read()
    if not ret:
        break
    pass

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7,6),None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv.drawChessboardCorners(img, (7,6), corners2,ret)
        cv.imshow('img',img)
        cv.waitKey(500)
    pass

cv.destroyAllWindows()