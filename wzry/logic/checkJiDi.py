import cv2
import numpy as np
from wzry.logic import initThumbnail


def checkWin(imCurrentFrame):

    imCurrentFrame[:529, :938] = 0
    imCurrentFrame[:385] = 0
    imCurrentFrame[:, 565] = 0

    red_pic = sim_pic(imCurrentFrame, initThumbnail.red)
    blue_pic = sim_pic(imCurrentFrame, initThumbnail.blue)

    image, contours, hierarchy = cv2.findContours(red_pic, 1, 2)
    if contours:
        red_square = max(cv2.contourArea(i) for i in contours)
    else:
        red_square = 0

    image, contours, hierarchy = cv2.findContours(blue_pic, 1, 2)
    if contours:
        blue_square = max(cv2.contourArea(i) for i in contours)
    else:
        blue_square = 0
    # print(red_square,blue_square)
    if red_square > blue_square:
        # 红队败
        return 0
    else:
        # 蓝队败
        return 1

def sim_pic(frame, colors):
    im = np.zeros(frame.shape[:2]).astype(np.uint8)
    for color in colors:
        r = abs(frame[:, :, 2].astype(np.int) - color[0])
        g = abs(frame[:, :, 1].astype(np.int) - color[1])
        b = abs(frame[:, :, 0].astype(np.int) - color[2])
        im[r + g + b < 100] = 255
    return im

