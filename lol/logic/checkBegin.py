import cv2

from lol.logic import initThumbnail


def checkLeftAndRightBegin(imCurrentFrame):
    #print("check begin")
    #res1 = cv2.matchTemplate(imCurrentFrame[5:71, 561:633], initThumbnail.left_head, cv2.TM_SQDIFF_NORMED)
    #res1 = cv2.minMaxLoc(res1)[0]
    #res2 = cv2.matchTemplate(imCurrentFrame[5:71, 1279:1347], initThumbnail.right_head, cv2.TM_SQDIFF_NORMED)
    #res2 = cv2.minMaxLoc(res2)[0]

    #new middle size: 222 * 60
    #if res1 + res2 < 0.1:
    res3 = cv2.matchTemplate(imCurrentFrame[0:60, 856:856+222], initThumbnail.middle_head, cv2.TM_SQDIFF_NORMED)
    res3 = cv2.minMaxLoc(res3)[0]
    if res3 < 0.1:
        return True

    return False