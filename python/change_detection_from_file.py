#! /home/smithw/.tensorflow2/bin/python
# use python in (TF2) venv on acer: opencv installed there

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


def get_file_list(filepath, file_range, num):
    # file_range: provides a subset of all files at filepath, if desired
    
    mov_list = os.listdir(filepath)
    mov_list.sort()

    ind0 = mov_list.index(file_range[0])
    ind1 = mov_list.index(file_range[1])
    dd   = mov_list[ind0 : ind1 + 1]
    # return a list of lists: each sublist is num files long,
    # but the last sublist may be less than num files long
    return [dd[i:i + num] for i in range(0, len(dd), num)]


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
        INPUT VIDEOS: the information below is relevant to the input videos to be processed
         data['basedir']:    str: full path to base directory of video files
         data['subdir']:     str: subdirectory to input video files: ALSO used for 'resdir' subdir
         data['proc_range']: tuple of str: (starting_video_name, ending_video_name)
         data['mask']:       str: path and name of motion-ignore mask used; 'None' if no mask
         data['resdir']:     str: full or relative base path to where video results are to be stored
         data['desc']:       str: brief description of day (eg, calm, windy, raining, etc.)
         data['fps_of_vid']  int: frames/sec of input vids: output vids' fps are set to this
         data['sec_per_vid'] int: seconds per video of the input vids
         data['num']:        int: number of input vids to process per output motion-detect vid
         data['skip']:       int: num of overlap frames if overlap exists between consecutive vids
         data['row_frac']:   float: 0 to 1, mask out timestamp rows (eg, 0.9 to mask out lower 10%)
         data['col_frac']:   float: 0 to 1, mask out timestamp cols (eg, 0.3 to mask out left  30%)
                             (taken together, a rectangle in the lower-left frame would be masked)
        PROCESSING PARAMS
         para['scale']       float: scale for processing size and final video size (eg, 0.5)
         para['framecount']: int: num of background frames to get before motion detection starts
         para['blur_size']:  int: blur kernel size: blur_size x blur_size
         para['t_val']:      int: thresh for detection: a critical parameter re: Pd vs FA
         para['alpha']:      float: 0 to 1; backgrnd = (1 - alpha) * backgrnd + alpha * new_frame
         para['frameshow']:  boolean: True shows frames as they are processed, but it is slow
        '''
        self.filepath   = os.path.join(data['basedir'], data['subdir'])
        self.filenames  = get_file_list(self.filepath, data['proc_range'], data['num'])
        self.skip       = data['skip']
        self.base       = os.path.join(data['resdir'], data['subdir'])
        self.fps        = data['fps_of_vid']
        self.blur_size  = para['blur_size']
        self.framecount = para['framecount']
        self.t_val      = para['t_val']
        self.frameshow  = para['frameshow']
        self.mask       = None
        self.md         = MotionDetector(alpha=para['alpha'])

        fullpath = os.path.join(self.filepath, self.filenames[0][0]) # first video
        vid      = cv2.VideoCapture(fullpath)
        
        ret, frame = vid.read() # first frame of first video to get frame size
        
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
    
        # block out ROVE timestamp location whether mask or no mask
        self.row_mask = int(data['row_frac'] * self.height)
        self.col_mask = int(data['col_frac'] * self.width)

        # rescale mask if it is input
        if data['mask'] is not None:
            maskpath = os.path.join(self.filepath, data['mask'])
            mask = cv2.imread(maskpath, 0) # 0 means read as grayscale
            self.mask = cv2.resize(mask, (self.width, self.height),
                                   interpolation=cv2.INTER_NEAREST)

        print('\nNew Video Dimensions: {} x {}'.format(self.width, self.height))

        self.video_out = VideoOutput(self.width, self.height, self.fps)


    def run(self):
        
        t0    = time()
        total = 0  # total frame count over all video files
        if not os.path.exists(self.base):
            os.makedirs(self.base)
            print('\nCreated output directory {}\n'.format(self.base))
        
        # loop over video groups: one motion-detect video produced per group
        for video_group in self.filenames:
            
            # create new video capture object here
            savenam = '{}-{}.mp4'.\
                      format(video_group[0][0:16], video_group[-1][5:16])
            savenam = os.path.join(self.base, savenam)

            print('\nNext file to save: {}'.format(savenam))
            new_video_out = self.video_out.new_writer(savenam)

            # loop over videos within a group
            for input_video in video_group:

                fullpath = os.path.join(self.filepath, input_video)
                vid      = cv2.VideoCapture(fullpath)
                count    = 0  # initialize skip count    

                print('processing {}'.format(fullpath))

                while vid.isOpened():

                    ret, frame = vid.read()
                    if not ret:
                        break  # end of input video file

                    # skip over redundant frames at beginning of video splice
                    # if overlap exists
                    if count < self.skip:
                        count += 1
                        continue

                    frame = cv2.resize(frame, (self.width, self.height), 
                                       interpolation=cv2.INTER_LINEAR)

                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    gray = cv2.GaussianBlur(gray, 
                                            (self.blur_size, self.blur_size), 0)

                    # if motion-ignore mask is input, it has already been resized
                    if self.mask is not None:
                        #gray = cv2.bitwise_and(gray, gray, mask=self.mask)
                        gray = cv2.bitwise_and(gray, self.mask) # this is a better result

                        # diagnostic check on the masking: remove before flight
                        #while True:
                        #   cv2.imshow('masked', gray)
                        #   if cv2.waitKey(1) == ord('q'):
                        #       break

                    # mask out timestamp: this may be redundant if mask already masks this
                    gray[self.row_mask:, 0:self.col_mask] = 0

                    if total > self.framecount:

                        motion = self.md.detect(gray, tVal=self.t_val)

                        if motion is not None:
                            (thresh, (minX, minY, maxX, maxY)) = motion
                            cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                                          (0, 255, 255), 1)

                            # write new video file with just the frames with motion
                            new_video_out.write(frame)

                    self.md.update_background(gray)
                    total += 1

                    if self.frameshow:
                        cv2.imshow('frame', frame)
                        if cv2.waitKey(1) == ord('q'):
                            break

                vid.release()

            # release the output video object for this pass of the loop
            new_video_out.release()

        dt = time() - t0
        self.cleanup()
        
        return total, dt  # total frames processed, time (seconds) to process


    def cleanup(self):
        cv2.destroyAllWindows()


    def show_filelist(self):
        print('\nFiles to be processed and their grouping:')
        for j in self.filenames:
            print()
            for k in j:
                print(k)
        print()
        self.cleanup()



if __name__=='__main__':


    test_wi_mask  =  {'basedir':     '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house',
                      'subdir':      '2022_0128',
                      'proc_range':  ('2022_0128_104425_003.MP4', '2022_0128_111425_013.MP4'),
                      'resdir':      'tmp',
                      'desc':        'very windy day! needs a mask',
                      'mask':        'masks/2022_0128_104425_003.MP4.mask_2022_0201_212059.jpg',
                      'fps_of_vid':   30,
                      'sec_per_vid':  180,
                      'num':          3,
                      'skip':         30,
                      'row_frac':     0.9,
                      'col_frac':     0.3}

    test_no_mask  =  {'basedir':      '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house',
                      'subdir':       '2022_0201',
                      'proc_range':   ('2022_0201_095506_492.MP4', '2022_0201_102506_502.MP4'),
                      'resdir':       'tmp',
                      'desc':         'calm day',
                      'mask':         None,
                      'fps_of_vid':   30,
                      'sec_per_vid':  180,
                      'num':          3,
                      'skip':         30,
                      'row_frac':     0.9,
                      'col_frac':     0.3}

    # change-detection parameters
    params_default = {'scale':        0.5,
                      'framecount':   15,
                      'blur_size':    3,
                      't_val':        5,
                      'alpha':        0.5,
                      'frameshow':    False}

    data   = test_wi_mask
    params = params_default

    vp     = VideoProcess(data, params)
    
    # show videos to be processed and their groupings
    vp.show_filelist()

    total, dt = vp.run()

    print('\n{:0.2f} sec ({:0.2f} min) to process {} frames, or {:0.2f} frames/sec\n'.\
          format(dt, dt/60., total, total/dt))
