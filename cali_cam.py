LINE = 60*"#"
print( "Hello ...")

import numpy as np, cv2 as cv, glob
from time import sleep

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
# Find the chess board corners
patternSize = (7, 6)
patternSize = (6, 10)
patternSize = (5, 8)
patternSize = (4, 4)
patternSize = (3, 4)

pattern_col = patternSize[0]
pattern_row = patternSize[1]
patternSize = (pattern_col, pattern_row)

objp = np.zeros((pattern_col*pattern_row,3), np.float32)
objp[:,:2] = np.mgrid[0:pattern_col, 0:pattern_row].T.reshape(-1,2)

print( f"Pattern size = {patternSize}")
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('*.jpg')

def gstream_pipeline( camera_id=0, width=1920, height=1080, framerate=10, flip_method=0 ):
    return f"nvarguscamerasrc sensor-id={camera_id} ! video/x-raw(memory:NVMM), width=(int){width}, height=(int){height}, format=(string)NV12, framerate=(fraction){framerate}/1 ! nvvidconv flip-method={flip_method} ! video/x-raw, width=(int){width}, height=(int){height}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"  
pass

size_factor = 2
gstream_info = gstream_pipeline(width=1280//size_factor, height=960//size_factor)

print( f"GSTREAM = {gstream_info}" )
print( LINE, flush=True )
print(); print()

cap = cv.VideoCapture(gstream_info, cv.CAP_GSTREAMER)

idx = 0 
corners_Found = False
img = None
gray = None 

while cap.isOpened() and not corners_Found :
    ret, img = cap.read()
    if not ret:
        break
    pass

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, corners = cv.findChessboardCorners(gray, patternSize, None)

    if corners is not None :
        print( f"[{idx:04d}] Corners len = {len(corners)}", flush=True)
        corners_Found = True
    else :
        print( f"[{idx:04d}] Corners not found!" )
    pass

    # If found, add object points, image points (after refining them)
    if ret :
        # termination criteria
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001) 

        corners2 = cv.cornerSubPix(gray,corners, (11,11),(-1,-1), criteria)
        # Draw and display the corners
        img = cv.drawChessboardCorners(img, patternSize, corners2, ret)
        cv.imshow('img', img) 
        
        do_append = True  
        if do_append : 
            objpoints.append(objp)
            imgpoints.append(corners2)
        pass
    else :
        cv.imshow('img', gray) 
    pass

    if cv.waitKey(1) in [ ord('q'), 27 ]:
        break
    pass
    idx += 1
pass

while not ( cv.waitKey(1) in [ ord('q'), 27 ] ):
    sleep( 1 )
pass

if gray is not None :
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

    h, w = gray.shape[:2]
    newcameramtx, roi=cv.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

    # undistort
    # undistort
    dst = cv.undistort(img, mtx, dist, None, newcameramtx)

    # crop the image
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]
    cv.imwrite('calibresult.png', dst)

    cv.imshow('img', dst)
pass

while not ( cv.waitKey(1) in [ ord('q'), 27 ] ):
    sleep( 1 )
pass

cv.destroyAllWindows()