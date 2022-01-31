#! /home/smithw/.tensorflow2/bin/python
# use python in (TF2) venv: opencv installed there

# pygame.mask.py
# WESmith 01/30/22
# use pygame to make motion-detection ignore mask

import pygame as pg
import cv2
import numpy as np

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
        print("Can't receive frame (stream end?). Exiting ...")
        vid.release()
        sys.exit(0)

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


imname   = 'results/tmp.jpg'
maskname = 'results/mask.jpg'

filepath  = '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house/'
filename  = '2022_0128_104425_003.MP4'
scale     = 1.0 # scale later after mask has been made
ymin      =  10 # min image pixel value, used for mask thresholding
ymax      = 250 # max image pixel value, used for mask thrsholding
radii     = [2, 4, 6, 8, 10, 16, 32] # possible radii of blobs
radindx   = 0

color     = BLACK  #YELLOW # color of mask

# draw mask on full size imageL scale = 1
size, frame = get_frame(filepath + filename, scale=scale, ymin=ymin)

cv2.imwrite(imname, frame)

print('\nmin, max of grayscale image: {}, {}\n'.\
      format(np.min(frame), np.max(frame)))

# don't use resizable frame at present: image is not resized
screen  = pg.display.set_mode(size) # , flags=pg.RESIZABLE)
myimage = pg.image.load(imname).convert()

screen.blit(myimage, (0, 0))

isPressed = False
run = True
while run:

    for event in pg.event.get():

        if event.type == pg.MOUSEBUTTONDOWN:
            isPressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            isPressed = False
        elif event.type == pg.MOUSEMOTION and isPressed:
            x, y = pg.mouse.get_pos()
            drawCirc(screen, x, y, rad=radii[radindx], color=color)
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE: # backspace to clear mask
                screen.blit(myimage, (0,0))
            if event.key == pg.K_s:  # s to save mask
                print('saving mask to {}'.format(maskname))
                pg.image.save(screen, maskname)
            if event.key == pg.K_UP: # arrow up to cycle thru blob radii
                radindx += 1
                radindx = radindx % len(radii)
                print('blob radius is now {}'.format(radii[radindx]))
            if event.key == pg.K_q:  # q to quit
                run = False

        if event.type == pg.QUIT: # hit 'X' in upper-right menu to quit
            run = False

    pg.display.flip()


print('\npyGame gently quit...\n')

pg.quit()

mask = cv2.imread(maskname, 0) # 0 means read as grayscale

ret, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

mask = cv2.erode(mask,  None, iterations=3)
mask = cv2.dilate(mask, None, iterations=3)

print('\nmin, max of mask image: {}, {}\n'.\
      format(np.min(mask), np.max(mask)))

while True:
    cv2.imshow('mask', mask)
    if cv2.waitKey(1) == ord('q'):
                        break

print('writing {}'.format(maskname))

cv2.imwrite(maskname, mask)
