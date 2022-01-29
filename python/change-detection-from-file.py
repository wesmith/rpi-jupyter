#! /home/smithw/.tensorflow2/bin/python
# use python in (TF2) venv: opencv installed there

# change-detection-from-file.py
# WESmith 01/27/22
# test change-deteciton algorithms using video files
# initial change-detection architecture from Adrian Rosebrock

import cv2
import numpy as np
import os, sys
from   time import time


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


def get_file_list(filepath, names):

    mov_list = os.listdir(filepath)
    mov_list.sort()

    ind0, ind1 = mov_list.index(names[0]), mov_list.index(names[1])
    return mov_list[ind0 : ind1 + 1]


class VideoOutput():

    def __init__(self, width, height, fps):

        self.width  = width
        self.height = height
        self.fps    = fps
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    def new_writer(self, savname):

        return cv2.VideoWriter(savenam, self.fourcc, self.fps,
                               (self.width, self.height))


class VideoProcess():

    def __init__(self, filepath, names, skip, row_frac, col_frac,
                 fps, scale, base, 
                 framecount=15, blur_size=3, t_val=5, alpha=0.2, frameshow=False):
        '''
        INPUT VIDEOS
         filepath:     full path to video files
         names:        tuple: (starting_videofile_name, ending_videofile_name)
         skip:         number of overlap frames if there is overlap between consecutive videos
         row_frac:    
         col_frac:
        OUTPUT VIDEO
         fps:
         scale:
         base:
        PROCESSING PARAMS
         framecount:
         blur_size:
         t_val:
         alpha:
         frameshow:
        '''
        self.filepath   = filepath
        self.filenames  = get_file_list(self.filepath, names)
        self.skip       = skip
        self.blur_size  = blur_size
        self.framecount = framecount
        self.t_val      = t_val
        self.frameshow  = frameshow

        self.md         = MotionDetector(alpha=alpha)

        fullpath = self.filepath + self.filenames[0] # first video
        vid      = cv2.VideoCapture(fullpath)
        
        ret, frame = vid.read() # first frame to get frame size
        
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            vid.release()
            sys.exit(0)
            
        vid.release()

        print('\nOriginal Video Dimensions: {} x {}'.\
              format(frame.shape[1], frame.shape[0]))

        # final frame size
        self.width  = int(frame.shape[1] * scale)
        self.height = int(frame.shape[0] * scale)
    
        self.row_mask = int(row_frac * self.height)
        self.col_mask = int(col_frac * self.width)

        print('\nNew Video Dimensions: {} x {}'.format(self.width, self.height))

        savenam = '{}/{}-{}.mp4'.\
                  format(base, self.filenames[0][0:16], self.filenames[-1][5:16])
        fourcc   = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(savenam, fourcc, fps, 
                                   (self.width, self.height))
 
    def run(self):
        
        total = 0  # total frame count over all video files
        
        # video-file loop
        for num in range(0, len(self.filenames)):
            
            fullpath = self.filepath + self.filenames[num]
            vid      = cv2.VideoCapture(fullpath)
            count    = 0  # initialize skip count    
            
            print('\nprocessing {}'.format(fullpath))

            while vid.isOpened():

                ret, frame = vid.read()
                if not ret:
                    break  # end of input video file

                # skip over redundant frames at beginning of video splice if overlap exists
                if count < self.skip:
                    count += 1
                    continue

                frame = cv2.resize(frame, (self.width, self.height), 
                                   interpolation=cv2.INTER_LINEAR)

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, 
                                        (self.blur_size, self.blur_size), 0)

                gray[self.row_mask:, 0:self.col_mask] = 0  # mask out changing timestamp

                if total > self.framecount:

                    motion = self.md.detect(gray, tVal=self.t_val)

                    if motion is not None:
                        (thresh, (minX, minY, maxX, maxY)) = motion
                        cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 255, 255), 1)

                        # write new video file with just the frames with motion
                        self.out.write(frame)

                self.md.update_background(gray)
                total += 1

                if self.frameshow:
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) == ord('q'):
                        break

            vid.release()

        self.cleanup()
        
        return total  # total frames processed


    def cleanup(self):
        self.out.release()
        cv2.destroyAllWindows()


if __name__=='__main__':
    
    
    filepath  = '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house/'

    #filenames = ('2022_0126_150004_088.MP4', '2022_0126_150304_089.MP4')
    filenames = (('2022_0128_104124_002.MP4', '2022_0128_113824_021.MP4'),
                 ('2022_0128_114124_022.MP4', '2022_0128_123824_041.MP4'),
                 ('2022_0128_124124_042.MP4', '2022_0128_133829_061.MP4'))
    '''
                ('2022_0128_134129_062.MP4', ''),'2022_0128_133829_061.MP4'
                ('2022_0128_144128_082.MP4', ''),
                ('2022_0128_154128_102.MP4', ''),
                ('2022_0128_164128_122.MP4', ''),
                ('2022_0128_174127_142.MP4', ''))
    '''

    # change-detection parameters
    skip       =  30  # overlap frames between end of one video and beginning of next
    row_frac   =  0.9 # values to mask out changing timestamp in lower-left corner
    col_frac   =  0.3
    fps        = 30   # frames/sec for final video of detected change
    scale      =  0.5 # scale for processing and final video size
    base       = 'results'
    framecount = 15   # background history length in frames
    blur_size  =  3   # background blur
    t_val      =  5   # threshold for detection
    alpha      =  0.2 # weighting between current frame and background
    frameshow  = False # True shows frames as they are processed, but it slows things down

    vp = VideoProcess(filepath, filenames, skip, row_frac, col_frac,
                        fps, scale, base, 
                        framecount=framecount, blur_size=blur_size,
                        t_val=t_val, alpha=alpha, frameshow=frameshow)
    t0 = time()

    total = vp.run()

    dt = time() - t0

    print('\nIt took {} sec to process {} total frames, or {} frames/sec\n'.\
          format(dt, total, total/dt))