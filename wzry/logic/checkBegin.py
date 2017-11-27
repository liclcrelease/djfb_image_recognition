import cv2

from wzry.logic import initThumbnail


def checkLeftAndRightBegin(imCurrentFrame):
    #print("check begin")
    rpic1 = imCurrentFrame[0:93, 343:430]
    for i in range(355, 391):
        for j in range(22, 77):
            imCurrentFrame[j, i] = 0

    rpic2 = imCurrentFrame[0:93, 1508:1596]
    for i in range(1542, 1583):
        for j in range(22, 77):
            imCurrentFrame[j, i] = 0

    res = cv2.matchTemplate(rpic1, initThumbnail.leftPic, cv2.TM_SQDIFF_NORMED)[0][0]
    res1 = cv2.matchTemplate(rpic2, initThumbnail.rightPic, cv2.TM_SQDIFF_NORMED)[0][0]

    # 匹配到白框
    if res + res1 < 0.01:
        return True

    return False