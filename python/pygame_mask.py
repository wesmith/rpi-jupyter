#! /home/smithw/.tensorflow2/bin/python
# use python in (TF2) venv: opencv installed there

# pygame.mask.py
# WESmith 01/30/22
# use pygame to make motion-detection ignore mask

import pygame as pg
import cv2

pg.init()


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


def drawCirc(screen, x, y, rad, color):
    pg.draw.circle(screen, color, (x, y), rad)


RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

imname = 'results/tmp.jpg'

filepath  = '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house/'
filename  = '2022_0128_104425_003.MP4'
scale     = 0.5

size, frame = get_frame(filepath + filename, scale)

cv2.imwrite(imname, frame)

screen  = pg.display.set_mode(size)
myimage = pg.image.load(imname).convert()

screen.blit(myimage, (0, 0))

isPressed = False
run = True
while run:
    
    pg.display.flip()
    for event in pg.event.get():
        #print('event.type: {}'.format(event.type))
        # 'quit' is by pressing 'cross' in upper-right window menu
        if event.type == pg.QUIT:
            run = False


'''
screen = pg.display.set_mode((500, 500))

def drawCirc(screen, x, y, rad):
    pg.draw.circle(screen, BLUE, (x, y), rad)
    
while True:
    
    for event in pg.event.get():
        
        if event.type == pg.MOUSEBUTTONDOWN:
            isPressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            isPressed = False
        elif event.type == pg.MOUSEMOTION and isPressed:
            x, y = pg.mouse.get_pos()
            drawCirc(screen, x, y, rad=10)

    pg.display.flip()  # flip() refreshes the screen for each pass
'''

print('\npyGame gently quit...\n')

pg.quit()