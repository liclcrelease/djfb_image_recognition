import cv2
from lol.logic import initThumbnail

def checkChoose(imCurrentFrame):
    listRet = []

    # 各种像素值
    a = [150, 260, 371, 481, 592]
    h = 44
    left_x = 37
    right_x = 1838

    left_circle_1 = [45, 5]
    left_circle_2 = [45, 40]

    circle_radius = 14

    right_circle_1 = [-1, 5]
    right_circle_2 = [-1, 40]

    left_rec = [18, 27]

    right_rec = [23, 27]

    # 匹配双方英雄，事先把技能的圆形和等级的矩形变成黑色
    for k in a:
        circle_y = k + left_circle_1[1]
        circle_x = left_x + left_circle_1[0]
        for i in range(circle_y - 14, circle_y + 15):
            for j in range(circle_x - 14, circle_x + 15):
                if (j - circle_x) ** 2 + (i - circle_y) ** 2 <= circle_radius ** 2:
                    imCurrentFrame[i, j] = 0

        circle_y = k + left_circle_2[1]
        circle_x = left_x + left_circle_2[0]

        for i in range(circle_y - 14, circle_y + 15):
            for j in range(circle_x - 14, circle_x + 15):
                if (j - circle_x) ** 2 + (i - circle_y) ** 2 <= circle_radius ** 2:
                    imCurrentFrame[i, j] = 0

        for i in range(k, k + 44):
            for j in range(left_x, left_x + 44):
                if i >= k + left_rec[1] and j <= left_x + left_rec[0]:
                    imCurrentFrame[i, j] = 0

        circle_y = k + right_circle_1[1]
        circle_x = right_x + right_circle_1[0]
        for i in range(circle_y - 14, circle_y + 15):
            for j in range(circle_x - 14, circle_x + 15):
                if (j - circle_x) ** 2 + (i - circle_y) ** 2 <= circle_radius ** 2:
                    imCurrentFrame[i, j] = 0

        circle_y = k + right_circle_2[1]
        circle_x = right_x + right_circle_2[0]

        for i in range(circle_y - 14, circle_y + 15):
            for j in range(circle_x - 14, circle_x + 15):
                if (j - circle_x) ** 2 + (i - circle_y) ** 2 <= circle_radius ** 2:
                    imCurrentFrame[i, j] = 0

        for i in range(k, k + 44):
            for j in range(right_x, right_x + 44):
                if i >= k + right_rec[1] and j >= right_x + right_rec[0]:
                    imCurrentFrame[i, j] = 0

    tt = []
    for hero in initThumbnail.heroes_left:
        left = imCurrentFrame[a[0] - 20:a[-1] + h + 20, left_x - 20:left_x + h + 20]
        right = imCurrentFrame[a[0] - 20:a[-1] + h + 20, right_x - 20:right_x + h + 20]
        res = cv2.matchTemplate(left, initThumbnail.heroes_left[hero], cv2.TM_SQDIFF_NORMED)
        r1 = cv2.minMaxLoc(res)
        res = cv2.matchTemplate(right, initThumbnail.heroes_right[hero], cv2.TM_SQDIFF_NORMED)
        r2 = cv2.minMaxLoc(res)
        if r1[0] < r2[0]:
            r = list(r1)
            r[2] = (r[2][0] + left_x - 20, r[2][1] + a[0] - 20)
        else:
            r = list(r2)
            r[2] = (r[2][0] + right_x - 20, r[2][1] + a[0] - 20)

        mi = float('inf')
        te = [[left_x, x] for x in a] + [[right_x, x] for x in a]
        for idx, rr in enumerate(te, 1):
            if (r[2][0] - rr[0]) ** 2 + (r[2][1] - rr[1]) ** 2 < mi:
                mi = (r[2][0] - rr[0]) ** 2 + (r[2][1] - rr[1]) ** 2
                t = idx

        tt.append((r[0], r[2], hero, t, mi))
    tt.sort()
    x = set()
    re = []
    for i in tt:
        if i[3] not in x and i[4] < 100:
            re.append(i)
            x.add(i[3])
    re.sort(key=lambda y: y[3])

    # 左一到左五，右一到右五英雄
    for i in re:
        listRet.append(i)

    return listRet

