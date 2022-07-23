"""Capture video from camera."""
import cv2 as cv
from time import sleep

print( "Hello ..." )

cap = cv.VideoCapture(0)

for i in range( 100 ) :
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    cv.imshow('frame', frame)
    sleep( 0.1 )
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()

print( "Good bye!" )
