#!/usr/bin/python3

# video_roi_bounce.py
# WESmith 1/4/22
# copied pieces from McWhorter's openCV10-ROI_Bounce.py and
# the 'rpi cookbook' ch_08_coin_count_test.py

# imutils functions seem to have longer latency than
# native cv2 functions

import cv2
#from imutils.video import VideoStream
#from imutils import resize
print('openCV version {}'.format(cv2.__version__))

'''
vs = VideoStream(src=0).start()

while True:
    img = vs.read()
    img = resize(img, width=400)
    cv2.imshow('image', img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
vs.stop()
cv2.destroyAllWindows()
'''
scale = 2
dispW = 320 * scale
dispH = 240 * scale
flip = 0

# the following is for the webcam: 
# use '1' if picam is used in slot '0'
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,  dispW)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, dispH)
camNam = 'webCam'
'''
actual_dispW = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
actual_dispH = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
print('')
print('ACTUAL DISPLAY WIDTH, HEIGHT:', 
      actual_dispW, actual_dispH)
'''
BW   = int(0.3 * dispW)
#BH   = int(0.3 * dispH)
BH   = BW # WS
posX = int(dispW/2) # WS
posY = int(dispH/2) # WS
dx   = 8
dy   = 8

while True:
    ret, frame = cam.read()
    
    roi = frame[posY:posY + BH, posX:posX + BW].copy()
    
    # WS mod to invert main BW frame
    frame = -frame + 255

    # this collapses 3 RGB channels to 1 BW channel
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # this expands the 1 BW channel to 3 BW channels
    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    
    # this broadcasts the 3 RGB roi channels back into
    # the three BW channels
    frame[posY:posY + BH, posX:posX + BW] = roi
    
    cv2.rectangle(frame, (posX, posY), 
                  (posX + BW, posY + BH), 
                  (0, 0, 0), 2)
                
    cv2.imshow(camNam, frame)
    '''
    cv2.moveWindow(camNam, 0, 0)
    '''
    posX += dx
    posY += dy
    if posX <= 0 or posX + BW >= dispW: dx *= -1
    if posY <= 0 or posY + BH >= dispH: dy *= -1
    
    if cv2.waitKey(1) == ord('q'):
        break
        
cam.release()
cv2.destroyAllWindows()