#! /home/smithw/.tensorflow2/bin/python
# use python in (TF2) venv: opencv installed there

# change-detection-from-file.py
# WESmith 01/27/22
# test change-deteciton algorithms using video files
# initial change-detection architecture from Adrian Rosebrock

import cv2
import numpy as np
import sys


class MotionDetector():

    def __init__(self, alpha=0.5):
        
        self.alpha      = alpha # weight for new frame
        self.background = None
        

    def update_background(self, frame):
        
        if self.background is None:
            self.background = frame.copy().astype("float")
            return

        # background = (1 - alpha) * background + alpha * frame
        cv2.accumulateWeighted(frame, self.background, self.alpha)
        

    def detect(self, frame, tVal=25):
		# compute the abs difference between the background model
		# and the current frame, then threshold the delta image
        delta  = cv2.absdiff(self.background.astype("uint8"), frame)
        thresh = cv2.threshold(delta, tVal, 255, cv2.THRESH_BINARY)[1]
		# perform a series of erosions and dilations to remove small
		# blobs
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # find contours in the thresholded image and initialize the
		# minimum and maximum bounding box regions for motion
        # WS mods to line
        contours, tree = cv2.findContours(thresh.copy(), 
                                          cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)
        #print('number of contours: {}'.format(len(contours)))  # WS mod
        #print('contours {}\n\n'.format(contours))
        
        #cnts = imutils.grab_contours(cnts) # WS replace with cv2?
        (minX, minY) = ( np.inf,  np.inf)
        (maxX, maxY) = (-np.inf, -np.inf)
        
        # if no contours were found, return None
        if len(contours) == 0:
            return None
        
		# otherwise, loop over the contours
        for c in contours:
			# compute the bounding box of the contour and use it to
			# update the minimum and maximum bounding box regions
            (x, y, w, h) = cv2.boundingRect(c)
            (minX, minY) = (min(minX, x), min(minY, y))
            (maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))
		# return a tuple of the thresholded image along
		# with the overall bounding box
        return (thresh, (minX, minY, maxX, maxY))



#filepath  = '/home/smithw/Devel/motioneyeos/captures/'
filepath  = '/home/smithw/Devel/test_videos/'
filenames = ['Camera1_2022-01-25-10-52-02.mp4',
    '2022_0126_153604_100.MP4',
    '2022_0126_160004_108.MP4',
    '2022_0126_170004_128.MP4',
    '2022_0127_154344_264.MP4',
    '2022_0127_154644_265.MP4',
    '2022_0127_155844_269.MP4',
    '2022_0127_160144_270.MP4']

num = 5

filepath += filenames[num]
savenam   = 'results/{}-changes.mp4'.format(filenames[num])

# change-detection parameters
scale      = 0.5 # scale for processing and final video size
blur_size  = 3   # background blur
framecount = 15  # background history length in frames
tVal       =  5  # threshold for detection: 25 isn't bad
rowFrac    = 0.9 # values to mask out changing timestamp in lower-left corner
colFrac    = 0.3

fps        = 30  # frames/sec for final video of detected change

vid = cv2.VideoCapture(filepath)
md  = MotionDetector(alpha=0.2)

ret, frame = vid.read() # get the first frame to get frame size
if not ret:
    print("Can't receive frame (stream end?). Exiting ...")
    vid.release()
    sys.exit(0)

print('Original Dimensions: {} x {}'.format(frame.shape[1], frame.shape[0]))
    
# final frame size
width  = int(frame.shape[1] * scale)
height = int(frame.shape[0] * scale)

rowMask = int(rowFrac * height)
colMask = int(colFrac * width)

print('New Dimensions: {} x {}'.format(width, height))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out    = cv2.VideoWriter(savenam, fourcc, fps, (width, height))

total  = 0

while vid.isOpened():
    
    ret, frame = vid.read()

    #if not ret:
    #    print("Can't receive frame (stream end?). Exiting ...")
    #    break
 
    #width  = int(frame.shape[1] * scale)
    #height = int(frame.shape[0] * scale)
  
    frame = cv2.resize(frame, (width, height), interpolation = cv2.INTER_LINEAR)
    
    #frame[rowMask:, 0:colMask] = 0  # mask out changing timestamp

    #print('New Dimensions : ', frame.shape)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)
    
    gray[rowMask:, 0:colMask] = 0  # mask out changing timestamp

    if total > framecount:

        motion = md.detect(gray, tVal=tVal)

        if motion is not None:
            (thresh, (minX, minY, maxX, maxY)) = motion
            cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 255, 255), 1)
            
            # write new video file with just the motion here
            out.write(frame)
            #cv2.imshow('frame', frame)

    md.update_background(gray)
    total += 1

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break

vid.release()
out.release()
cv2.destroyAllWindows()

    