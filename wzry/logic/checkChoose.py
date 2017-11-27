import cv2

from wzry.logic import initThumbnail


def checkChoose(imCurrentFrame):
    listRet = []
    tt=[]
    for hero in initThumbnail.heroes:
        left = imCurrentFrame[366:821, 0:71]
        right = imCurrentFrame[366:821, 1849:1920]
        res = cv2.matchTemplate(left, hero[0], cv2.TM_SQDIFF_NORMED)
        r1 = cv2.minMaxLoc(res)
        res = cv2.matchTemplate(right, hero[0], cv2.TM_SQDIFF_NORMED)
        r2 = cv2.minMaxLoc(res)
        if r1[0] < r2[0]:
            r = list(r1)
            r[2] = (r[2][0], r[2][1] + 366)
        else:
            r = list(r2)
            r[2] = (r[2][0] + 1849, r[2][1] + 366)

        mi = float('inf')
        t = 11
        for idx, rr in enumerate(initThumbnail.matchArray, 1):
            if (r[2][0] - rr[0]) ** 2 + (r[2][1] - rr[1]) ** 2 < mi:
                mi = (r[2][0] - rr[0]) ** 2 + (r[2][1] - rr[1]) ** 2
                t = idx
        # print(r[0],r[2],hero[1],t,mi)
        tt.append((r[0], r[2], hero[1], t, mi))
    tt.sort()
    x = set()
    re = []
    for i in tt:
        if i[3] not in x and i[4] < 100:
            re.append(i)
            x.add(i[3])
    re.sort(key=lambda y: y[3])
    for i in re:
        listRet.append(i[2])
    #print(listRet)
    return listRet

