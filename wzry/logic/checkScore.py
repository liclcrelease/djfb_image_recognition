
import cv2
from wzry.logic import initThumbnail


def checkScore(imCurrentFrame):
    retDict = {}
    listRes = []
    dictPos = {}

    for var in initThumbnail.left_kill:
        #res = cv2.matchTemplate(imCurrentFrame[36:72, 888:940],var[1],cv2.TM_SQDIFF_NORMED)[0][0]
        res1, res2, pos1, pos2 = getLeftMiddleRightCheckNum(imCurrentFrame[36:72, 878:930],var[1])
        dictPos[res1] = pos1
        dictPos[res2] = pos2
        listRes.append([res1, var[0]])
        listRes.append([res2, var[0]])

    leftKill = getNumByListAndPos(listRes,dictPos)

    listRes = []
    dictPos.clear()
    for var in initThumbnail.right_kill:
        #res = cv2.matchTemplate(imCurrentFrame[36:72, 988:1040], var[1], cv2.TM_SQDIFF_NORMED)[0][0]
        res1,res2,pos1,pos2 = getLeftMiddleRightCheckNum(imCurrentFrame[36:72, 988:1040], var[1])
        dictPos[res1] = pos1
        dictPos[res2] = pos2
        listRes.append([res1, var[0]])
        listRes.append([res2, var[0]])

    rightKill = getNumByListAndPos(listRes,dictPos)

    if leftKill is None or rightKill is None or\
            leftKill.__len__() <= 0 or rightKill.__len__() <= 0:
        return retDict

    retDict["leftKill"] = leftKill
    retDict["rightKill"] = rightKill

    #TODO
    return retDict

def getNumByListAndPos(listRes,dictPos):
    kill = ""
    listRes.sort(key=lambda x: x[0])

    if dictPos[listRes[0][0]] == "m":
        if listRes[0][0] < 0.15:
            print("not invalid number [{}][{}]".format(listRes[0], listRes[1]))
        else:
            kill = str(listRes[0][1])

    elif listRes[0][0] < 0.15 and listRes[1][0] < 0.15:
        # 倆個數字
        if dictPos[listRes[0][0]] == "m" or dictPos[listRes[1][0]] == "m" or \
                        dictPos[listRes[0][0]] == dictPos[listRes[1][0]]:
            print("not invalid number [{}][{}]".format(listRes[0], listRes[1]))
            return

        if dictPos[listRes[0][0]] == "l":
            kill = str(listRes[0][1]) + str(listRes[1][1])

        elif dictPos[listRes[0][0]] == "r":
            kill = str(listRes[1][1]) + str(listRes[0][1])

        else:
            print("not invalid number  1")
            return
    else:
        print("not invalid number  2")
        return

    return kill

def getLeftMiddleRightCheckNum(frame,template):

    res = []
    res1 = cv2.matchTemplate(frame[0:-1, 0:28], template, cv2.TM_SQDIFF_NORMED)[0][0]
    #cv2.imwrite("../wzry/bifen_left/test1.jpg",frame[0:-1, 0:28])
    res2 = cv2.matchTemplate(frame[0:-1, 27:52], template, cv2.TM_SQDIFF_NORMED)[0][0]
    #cv2.imwrite("../wzry/bifen_left/test2.jpg", frame[0:-1, 27:52])
    res3 = cv2.matchTemplate(frame[0:-1, 12:40], template, cv2.TM_SQDIFF_NORMED)[0][0]
    #cv2.imwrite("../wzry/bifen_left/test3.jpg", frame[0:-1, 12:40])

    resKey = {res1:"l",res2:"r",res3:"m"}
    res.append(res1)
    res.append(res2)
    res.append(res3)
    res.sort()

    return res[0],res[1],resKey[res[0]],resKey[res[1]]


