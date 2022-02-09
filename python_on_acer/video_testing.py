#! /home/smithw/.tensorflow2/bin/python
# use python in (TF2) venv on acer: opencv installed there

# video_testing.py
# WESmith 02/08/22
# test out opencv video processing for change detection, etc.

import cv2
import os, sys, time
import pickle
import pdb

class VideoGrab():

    def __init__(self, data, scale, row_frac=0.9, col_frac=0.3):
        
        self.filepath = os.path.join(data['filepath'], 
                                     data['subdir'])
        self.filename = data['filename']
        self.fullpath = os.path.join(self.filepath,
                                     self.filename)
        self.savebase = data['savebase']
        self.fps      = data['fps']
        self.start    = data['framestart']
        self.stop     = data['framestop']

        vid = cv2.VideoCapture(self.fullpath)
        
        # get first frame to get frame size
        ret, frame = vid.read()
        
        if not ret:
            print("Can't receive video frame. Exiting ...")
            vid.release()
            sys.exit()
            
        vid.release()

        print('\nOriginal Video Dimensions: {} x {}'.\
              format(frame.shape[1], frame.shape[0]))

        # final frame size
        self.width  = int(frame.shape[1] * scale)
        self.height = int(frame.shape[0] * scale)
    
        # block out ROVE timestamp location whether 
        # mask or no mask
        self.row_mask = int(row_frac * self.height)
        self.col_mask = int(col_frac * self.width)

        print('\nNew Video Dimensions: {} x {}'.\
              format(self.width, self.height))


    def select_and_save(self):
        '''
        select desired video range to analyze, and
        save it in a regular file
        '''
        filename = '{}_{}-{}.pkl'.\
                    format(self.filename, self.start, self.stop)
        savefile  = os.path.join(self.savebase, filename)                      
                                     
        vid_frames = []
        vid = cv2.VideoCapture(self.fullpath)
        n = 0
        delta_sec = 1./self.fps
        delta_ms  = int(1000. * delta_sec)
        
        while vid.isOpened():
            
            ret, frame = vid.read()

            if not ret or n >= self.stop:
                # end of video or have collected all frames
                break
            
            if n >= self.start:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
                frame = cv2.resize(frame, (self.width, self.height),
                                   interpolation=cv2.INTER_LINEAR)
                cv2.imshow('frame', frame)
                vid_frames.append(frame)
                if cv2.waitKey(delta_ms) == ord('q'):
                    break

            n += 1            

        cv2.destroyAllWindows()
        vid.release()
        print('saving {}'.format(savefile))
        pickle.dump(vid_frames, open(savefile, 'wb'))


def get_pickled_vid(filepath, filename, fps=30, display=False):
    
    fullpath   = os.path.join(filepath, filename)
    print('\nreading frame data from {}\n'.format(fullpath))
    
    vid_frames = pickle.load( open(fullpath, "rb"))
    
    if display:

        delta_ms   = int(1000./fps)
        for k in vid_frames:
            cv2.imshow('frame', k)
            if cv2.waitKey(delta_ms) == ord('q'):
                break
            
    return vid_frames


class VideoProcess():
    
    def __init__(self, filepath, filename, mask, alpha, tVal, blur,
                 fps, ncontours, framecount=25):
        '''
        filepath, filename:  location, name of pickled video-frame file
        fps:    desired frames/sec
        '''
        self.mask       = mask  # fullpath with name
        self.fps        = fps
        self.alpha      = alpha
        self.tVal       = tVal
        self.blur       = blur
        self.frames     = get_pickled_vid(filepath, filename)
        self.framecount = framecount
        self.delta_ms   = int(1000./self.fps)
        self.ncontours  = ncontours
        self.background = None


    def update_background(self, frame):
        
        if self.background is None:
            self.background = frame.copy().astype("float")
            return

        # background = (1 - alpha) * background + alpha * frame
        cv2.accumulateWeighted(frame, self.background, self.alpha)

        
    def run(self):

        for j, frame in enumerate(self.frames):
            
            gray = cv2.GaussianBlur(frame, (self.blur, self.blur), 0)

            if j > self.framecount:

                #cv2.imshow('background', self.background.astype('uint8'))

                delta = cv2.absdiff(self.background.astype("uint8"), gray)
                #cv2.imshow('diff', delta)
                
                thresh = cv2.threshold(delta, self.tVal, 255, cv2.THRESH_BINARY)[1]
                cv2.imshow('threshold', thresh)
                
                erode  = cv2.erode(thresh, None, iterations=1)
                dilate = cv2.dilate(erode, None, iterations=1)
                cv2.imshow('erode/dilate', dilate)
                
                contours, tree = cv2.findContours(thresh.copy(), 
                                          cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)
                
                areas = [cv2.contourArea(c) for c in contours]
                # sort areas, preserving original ordering in 'areas', largest first
                sorted_areas = sorted(areas, reverse=True)
                
                nn = 5
                largest_areas = sorted_areas[0:self.ncontours]  # keep largest contours
                
                largest_contours = []
                for k in largest_areas:
                    #indx = areas.index(k)
                    contour = contours[areas.index(k)]
                    largest_contours.append(contour)
                    
                cv2.drawContours(frame, largest_contours, -1, (255,255,255), 1)
                
                for c in largest_contours:
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)
                    
                cv2.imshow('contours', frame)

                #pdb.set_trace()

                if cv2.waitKey(self.delta_ms) == ord('q'):
                    break

            
            self.update_background(gray)


            

if __name__=='__main__':

    filepath = '/media/smithw/SEAGATE-FAT/dashcam/Movie'
    subdir   = '2022_0207'
    data_0207= {'filepath': '/media/smithw/SEAGATE-FAT/dashcam/Movie',
                'subdir':   '2022_0207',
                'filename': '2022_0207_111646_327.MP4',
                'framestart':      810,
                'framestop':       1740,
                'fps':       90,
                'savebase':  'pickled_vids',
                'desc':     'person walking and truck'}

    #filename = '2022_0207_113146_332.MP4' # people, vehicles
    
    data = data_0207
    
    #vt = VideoGrab(data, 0.5)
    #vt.select_and_save()
    
    mask      = '2022_0207_102546_310.MP4.mask_2022_0207_202618.jpg' 
    mask_path = '/media/smithw/SEAGATE-FAT/dashcam/Movie/2022_0207/masks'
    mask      = os.path.join(mask_path, mask)
    pkl_path  = 'pickled_vids'
    filename  = '2022_0207_111646_327.MP4_810-1740.pkl'
    alpha     = 0.2
    tVal      = 10
    blur      = 3
    ncontours = 3
    fps       = 30
    

    #dd = get_pickled_vid(pkl_path, filename, fps=30, display=True)

    
    vp = VideoProcess(pkl_path, filename, mask, alpha, tVal, blur,
                      fps, ncontours, framecount=15)
    
    vp.run()