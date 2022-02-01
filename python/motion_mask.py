#! /home/smithw/.tensorflow2/bin/python
# use python in (TF2) venv: opencv installed there

# motion_mask.py
# WESmith 01/30/22
# use pygame to make motion-detection ignore mask using a video frame

import pygame as pg
import cv2
import numpy as np
import sys


pg.init()

RED     = (255,   0,   0)
GREEN   = (  0, 255,   0)
BLUE    = (  0,   0, 255)
CYAN    = (  0, 255, 255)
MAGENTA = (255,   0, 255)
YELLOW  = (255, 255,   0)
WHITE   = (255, 255, 255)
BLACK   = (  1,   1,   1)  # experimenting with 'black' value

def get_frame(fullpath, scale=1, ymin=10, ymax=250):
    # get the first frame of desired video as guide to mask development

    #fullpath = self.filepath + self.filenames[0] # first video
    vid = cv2.VideoCapture(fullpath)

    ret, frame = vid.read() # get first frame

    if not ret:
        print("\nERROR: Can't get video frame from {}. Exiting ...\n".\
              format(fullpath))
        vid.release()
        sys.exit()

    vid.release()

    # final frame size
    width  = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)

    # resize frame
    frame = cv2.resize(frame, (width, height), 
                       interpolation=cv2.INTER_LINEAR)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # rescale 0 to 255 to ymin to ymax for later mask thresholding
    tmp  = gray.astype('float32')
    gray = (tmp * (ymax - ymin)/255 + ymin).astype('uint8')

    return (width, height), gray


def drawCirc(screen, x, y, rad=10, color=RED):
    pg.draw.circle(screen, color, (x, y), rad)


def run(filepath, videoname, scale=1.0, ymin=10, ymax=250, color=BLACK):
    '''
    filepath:  path to video files
    videoname: name of video to use for mask definition
    scale:     scale factor for image size (use 1.0 in this program: scale is
               handled later in the motion-detection program)
    ymin:      min image pixel value, used for mask thresholding
    ymax:      max image pixel value, used for mask thrsholding
    color:     color of mask (use BLACK for the thresholding method used here)
    '''
    radii     = [2, 4, 6, 8, 10, 16, 32] # possible radii of blobs
    radindx   = 5                        # blob-radius index at startup
    colors    = [BLACK, WHITE]
    colindx   = 0

    snapshot_name = filepath + videoname + '.snapshot.jpg'  # frame on which to build mask
    mask_name     = filepath + videoname + '.mask.jpg'      # mask name

    # draw mask on full size image: scale = 1:
    # much easier for user-defined mask delineation
    size, frame = get_frame(filepath + videoname, scale=scale, ymin=ymin, ymax=ymax)

    #print('\nmin, max of grayscale image: {}, {}\n'.\
    #     format(np.min(frame), np.max(frame)))

    cv2.imwrite(snapshot_name, frame)

    # don't use resizable frame at present: image is not resized
    screen  = pg.display.set_mode(size) # , flags=pg.RESIZABLE)
    myimage = pg.image.load(snapshot_name).convert()

    screen.blit(myimage, (0, 0))

    txt =  '\n\n************************\n'
    txt += 'mouse-down and drag to draw mask blobs\n'
    txt += 'up-arrow            to cycle thru blob sizes\n'
    txt += 'u                   to undo mask area with white erasure\n'
    txt += 'u again             to toggle back into mask mode'
    txt += 'backspace           to clear mask\n'
    txt += 's                   to save mask\n'
    txt += 'q or "close window" at upper right to quit\n'
    txt +=  '************************\n\n'
    print(txt)

    isPressed   = False
    keep_moving = True
    while keep_moving:

        for event in pg.event.get():

            if event.type == pg.MOUSEBUTTONDOWN:
                isPressed = True
            elif event.type == pg.MOUSEBUTTONUP:
                isPressed = False
            elif event.type == pg.MOUSEMOTION and isPressed:
                x, y = pg.mouse.get_pos()
                drawCirc(screen, x, y, rad=radii[radindx], color=colors[colindx])

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE: # backspace to clear mask
                    screen.blit(myimage, (0,0))
                if event.key == pg.K_s:  # s to save mask
                    print('saving mask to {}'.format(mask_name))
                    pg.image.save(screen, mask_name)
                if event.key == pg.K_UP: # arrow up to cycle thru blob radii
                    radindx += 1
                    radindx = radindx % len(radii)
                    print('blob radius is now {}'.format(radii[radindx]))
                if event.key == pg.K_u:
                    colindx += 1
                    colindx = colindx % len(colors)
                    print('toggling between masking and unmasking')
                if event.key == pg.K_q:  # q to quit
                    keep_moving = False

            if event.type == pg.QUIT: # hit 'X' in upper-right menu to quit
                keep_moving = False

        pg.display.flip()

    pg.quit()

    print('\npyGame gently quit...\n')

    mask = cv2.imread(mask_name, 0) # 0 means read as grayscale

    ret, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

    mask = cv2.erode(mask,  None, iterations=3)
    mask = cv2.dilate(mask, None, iterations=3)

    print('\nmin, max of mask image: {}, {}\n'.\
          format(np.min(mask), np.max(mask)))

    while True:
        cv2.imshow('mask', mask)
        if cv2.waitKey(1) == ord('q'):
                            break

    print('writing {}'.format(mask_name))

    cv2.imwrite(mask_name, mask)


if __name__=='__main__':

    filepath   = '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house/2022_0128/'
    videoname  = '2022_0128_104425_003.MP4'  #  01/28/22 was a very windy day

    run(filepath, videoname)
