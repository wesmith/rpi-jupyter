#! /home/smithw/.tensorflow2/bin/python
# use python in (TF2) venv: opencv installed there

# pygame.mask.py
# WESmith 01/30/22
# use pygame to make motion-detection ignore mask

import pygame as pg
import cv2

pg.init()

RED     = (255, 0,   0)
GREEN   = (0, 255,   0)
BLUE    = (0,   0, 255)
CYAN    = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW  = (255, 255, 0)

def get_frame(fullpath, scale):
    # get the first frame of desired video as guide to mask development

    #fullpath = self.filepath + self.filenames[0] # first video
    vid      = cv2.VideoCapture(fullpath)

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

    return (width, height), frame


def drawCirc(screen, x, y, rad=10, color=RED):
    pg.draw.circle(screen, color, (x, y), rad)


imname   = 'results/tmp.jpg'
maskname = 'results/mask.jpg'

filepath  = '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house/'
filename  = '2022_0128_104425_003.MP4'
scale     = 0.5
rad       = 10  # redius of blobs to draw as mask
radii     = [2, 4, 6, 8, 10, 16, 32] # possible radii of blobs
radindx   = 0
color     = YELLOW # color of mask

size, frame = get_frame(filepath + filename, scale)

cv2.imwrite(imname, frame)

screen  = pg.display.set_mode(size)
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
            if event.key == pg.K_UP: # arrow up to cycle thru radii
                radindx += 1
                radindx = radindx % len(radii)
                print('blob radius is now {}'.format(radii[radindx]))
            if event.key == pg.K_q:  # q to quit
                run = False

        #print('event type {}'.format(event.type))

        if event.type == pg.QUIT: # hit 'X' in upper-right menu to quit
            run = False

    pg.display.flip()


print('\npyGame gently quit...\n')

pg.quit()