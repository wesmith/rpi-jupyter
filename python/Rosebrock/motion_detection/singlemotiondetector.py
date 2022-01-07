# singlemotiondetector.py
# WESmith 01/06/22
# copied from 
# https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-# web-browser-html-page/ by Adrian Rosebrock

import numpy as np
import imutils
import cv2


class SingleMotionDetector():

    def __init__(self, accumWeight=0.5):
        self.accumWeight = accumWeight
        self.bg = None

    def update(self, image):
        if self.bg is None:
            self.bg = image.copy().astype("float")
            return
		# update the background model by accumulating the weighted
		# average
        cv2.accumulateWeighted(image, self.bg, self.accumWeight)

    def detect(self, image, tVal=25):
		# compute the abs difference between the background model
		# and the current image, then threshold the delta image
        delta  = cv2.absdiff(self.bg.astype("uint8"), image)
        thresh = cv2.threshold(delta, tVal, 255, cv2.THRESH_BINARY)[1]
		# perform a series of erosions and dilations to remove small
		# blobs
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # find contours in the thresholded image and initialize the
		# minimum and maximum bounding box regions for motion
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts) # WS replace with cv2?
        (minX, minY) = (np.inf, np.inf)
        (maxX, maxY) = (-np.inf, -np.inf)
        
        # if no contours were found, return None
        if len(cnts) == 0:
            return None
        
		# otherwise, loop over the contours
        for c in cnts:
			# compute the bounding box of the contour and use it to
			# update the minimum and maximum bounding box regions
            (x, y, w, h) = cv2.boundingRect(c)
            (minX, minY) = (min(minX, x), min(minY, y))
            (maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))
		# return a tuple of the thresholded image along
		# with bounding box
        return (thresh, (minX, minY, maxX, maxY))