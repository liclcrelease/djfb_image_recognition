import cv2
import numpy as np
from lol.logic import initThumbnail


def checkWin(imCurrentFrame):
    red_pic = sim_pic(imCurrentFrame, initThumbnail.red)
    blue_pic = sim_pic(imCurrentFrame, initThumbnail.blue)

    image, contours, hierarchy = cv2.findContours(red_pic, 1, 2)
    red_square = max(cv2.contourArea(i) for i in contours)

    image, contours, hierarchy = cv2.findContours(blue_pic, 1, 2)
    blue_square = max(cv2.contourArea(i) for i in contours)
    if red_square > blue_square:
        # 红队败
        return 0
    else:
        # 蓝队败
        return 1


def sim_pic(frame,colors):
    im=np.zeros(frame.shape[:2]).astype(np.uint8)
    for color in colors:
        r=abs(frame[:,:,2].astype(np.int)-color[0])
        g=abs(frame[:,:,1].astype(np.int)-color[1])
        b=abs(frame[:,:,0].astype(np.int)-color[2])
    #print(r.shape)
        im[r+g+b<100]=255
    return im
