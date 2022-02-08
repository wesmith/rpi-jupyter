#!/usr/bin/python3
# this program runs on the RPi4

# change-detection-from-stream.py
# WESmith 02/04/22
# this is the real-time version of 
# change_detection_from_file.py developed on the acer


import cv2
import numpy as np
import os, sys
from   time import time
from   datetime import datetime

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


class VideoOutput():

    def __init__(self, width, height, fps):

        self.width  = width
        self.height = height
        self.fps    = fps
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    def new_writer(self, savename):

        return cv2.VideoWriter(savename, self.fourcc, self.fps,
                               (self.width, self.height))

class VideoProcess():

    def __init__(self, data, para):
        '''
        VIDEO PARAMS:
         data['cam_num']      int: camera number (0 for picam, 1 for webcam)
         data['num_frames']   int: number of frames per motion-detection output video
         data['num_out_vids'] int: number of change-detection videos to create
         data['mask']:        str: path and name of motion-ignore mask used; 
                              'None' if no mask
         data['resdir']:      str: full or relative base path to where video 
                              results are to be stored
         data['subdir']:      str: subdir where video results are to be stored
         data['fps_of_vid']   int: frames/sec of output change-detect videos

        PROCESSING PARAMS
         para['scale']       float: scale for processing size and final video size (eg, 0.5)
         para['framecount']: int: num of background frames to get before motion 
                                  detection starts
         para['blur_size']:  int: blur kernel size: blur_size x blur_size
         para['t_val']:      int: thresh for detection: a critical parameter re: Pd vs FA
         para['alpha']:      float: 0 to 1; 
                                    backgrnd = (1 - alpha) * backgrnd + alpha * new_frame
         para['frameshow']:  boolean: True shows frames as they are processed, but it is slow
        '''
        self.cam_num    = data['cam_num']
        self.num_out    = data['num_out_vids']
        self.num_frames = data['num_frames']
        self.base       = os.path.join(data['resdir'], data['subdir'])
        self.fps        = data['fps_of_vid']
        self.blur_size  = para['blur_size']
        self.framecount = para['framecount']
        self.t_val      = para['t_val']
        self.frameshow  = para['frameshow']
        self.mask       = None
        self.md         = MotionDetector(alpha=para['alpha'])
        self.font       = cv2.FONT_HERSHEY_SIMPLEX

        
        vid      = cv2.VideoCapture(self.cam_num)
        
        ret, frame = vid.read() # get frame size
        
        if not ret:
            print("Can't receive video frame. Exiting ...")
            vid.release()
            sys.exit()
            
        vid.release()

        print('\nOriginal Video Dimensions: {} x {}'.\
              format(frame.shape[1], frame.shape[0]))

        # final frame size
        self.width  = int(frame.shape[1] * para['scale'])
        self.height = int(frame.shape[0] * para['scale'])

        # rescale mask if it is input
        if data['mask'] is not None:
            maskpath = os.path.join(self.filepath, data['mask'])
            mask = cv2.imread(maskpath, 0) # 0 means read as grayscale
            self.mask = cv2.resize(mask, (self.width, self.height),
                                   interpolation=cv2.INTER_NEAREST)

        print('\nNew Video Dimensions: {} x {}'.format(self.width, self.height))

        self.video_out = VideoOutput(self.width, self.height, self.fps)


    def run(self):
        
        vid = cv2.VideoCapture(self.cam_num) 
        
        t0    = time()
        overall_total = 0  # total frame count over all video files from the beginning
        if not os.path.exists(self.base):
            os.makedirs(self.base)
            print('\nCreated output directory {}\n'.format(self.base))
        
        num_videos = 0
        # keep looping over video generation until stopping criteria is met
        while num_videos < self.num_out:
            
            # create new video capture object here
            vidname = '{:%Y_%m%d_%H%M%S}_motion.mp4'.format(datetime.now())
            savenam = os.path.join(self.base, vidname)

            print('\nNext file to generate: {}'.format(savenam))
            new_video_out = self.video_out.new_writer(savenam)

            frame_count = 0        # count of frames with motion detections
            total_count = 0        # count of total frames attempted to be captured for this loop
            error_frame_count = 0  # count of frames that were not captured
            while frame_count < self.num_frames:

                ret, frame = vid.read()
                total_count += 1
                if not ret:
                    error_frame_count += 1
                    continue  # error: skip this frame

                frame = cv2.resize(frame, (self.width, self.height), 
                                   interpolation=cv2.INTER_LINEAR)

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                gray = cv2.GaussianBlur(gray, 
                                        (self.blur_size, self.blur_size), 0)

                # if motion-ignore mask is input, it has already been resized
                if self.mask is not None:
                    #gray = cv2.bitwise_and(gray, gray, mask=self.mask)
                    gray = cv2.bitwise_and(gray, self.mask) # this is a better result

                if overall_total > self.framecount:

                    motion = self.md.detect(gray, tVal=self.t_val)

                    if motion is not None:
                        (thresh, (minX, minY, maxX, maxY)) = motion
                        cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                                      (0, 255, 255), 1)
                        
                        # add timestamp to frame
                        timestamp = datetime.now()
                        txt = timestamp.strftime("%d %B %Y %I:%M:%S %p")
                        cv2.putText(frame, txt, (10, 10), self.font, 1.0,
                                    (255, 120, 255), 1) # light magenta

                        # write new video file with just the frames with motion
                        new_video_out.write(frame)
                        frame_count += 1

                self.md.update_background(gray)
                overall_total += 1

                if self.frameshow:
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(0) == ord('q'):
                        break

            # release the output video object for this pass of the loop
            new_video_out.release()
            num_videos += 1
            # ultimately put this into a log file
            print('Vid {} has {} dropped frames out of {} attempts'.\
                  format(vidname, error_frame_count, total_count))

        vid.release()
        
        dt = time() - t0
        self.cleanup()
        
        return overall_total, dt  # total frames processed, time (seconds) to process


    def cleanup(self):
        cv2.destroyAllWindows()


if __name__=='__main__':


    test_wi_mask  =  {
                      'subdir':      '2022_0204',
                      'resdir':      'tmp',
                      'mask':        'masks/2022_0128_104425_003.MP4.mask_2022_0201_212059.jpg',
                      'fps_of_vid':   30,
                      'sec_per_vid':  180,
                      'num':          3,
                      'skip':         30,
                      'row_frac':     0.9,
                      'col_frac':     0.3}

    test_no_mask  =  {'cam_num':      0,
                      'num_frames':   300,
                      'num_out_vids': 2,
                      'subdir':       '2022_0204',
                      'resdir':       'tmp',
                      'mask':         None,
                      'fps_of_vid':   30}

    # change-detection parameters
    params_default = {'scale':        0.25,
                      'framecount':   15,
                      'blur_size':    3,
                      't_val':        5,
                      'alpha':        0.5,
                      'frameshow':    False}

    data   = test_no_mask
    params = params_default

    vp     = VideoProcess(data, params)
    
    total, dt = vp.run()

    print('\n{:0.2f} sec ({:0.2f} min) to process {} frames, or {:0.2f} frames/sec\n'.\
          format(dt, dt/60., total, total/dt))
