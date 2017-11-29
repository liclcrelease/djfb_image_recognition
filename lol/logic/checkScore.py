
import cv2
from lol.logic import initThumbnail


def checkScore(imCurrentFrame,):

    dictRet = {}

    left_num = ocr_num(imCurrentFrame, initThumbnail.left_rentou, 15,"left")
    right_num = ocr_num(imCurrentFrame, initThumbnail.right_rentou, 15,"right")
    left_num_tower = ocr_small_num(imCurrentFrame, initThumbnail.left_tower, 10,"left")
    right_num_tower = ocr_small_num(imCurrentFrame, initThumbnail.right_tower, 10,"right")

    dictRet["leftKill"] = left_num
    dictRet["rightKill"] = right_num
    dictRet["leftTower"] = left_num_tower
    dictRet["rightTower"] = right_num_tower

    return dictRet


def match_num(im,num_pic,num,result,x_s,dis):
    if im.shape[0]<num_pic.shape[0] or im.shape[1]<num_pic.shape[1]:
        return
    res = cv2.matchTemplate(im, num_pic, cv2.TM_SQDIFF_NORMED)
    res = cv2.minMaxLoc(res)

    #[相似度(越小越相似),数字的位置，数字值]
    result.append([res[0], (res[2][0]+x_s,res[2][1]), num])

    #匹配左边的数字
    if res[2][0]>=dis:
        match_num(im[:,:res[2][0]], num_pic, num, result,x_s,dis)
    #匹配右边的数字
    if res[2][0]<=im.shape[1]-dis:
        match_num(im[:,res[2][0]+15:], num_pic, num, result,x_s+res[2][0]+15,dis)

#最终的数字
def ocr_num(frame,rect,width,leftOrRight):
    im=frame[rect[0]:rect[1],rect[2]:rect[3]]
    result = []
    result_num = ''
    left_x = 0
    right_x = 0
    if leftOrRight == "left":
        for num_pic in initThumbnail.bifen_new_left:
            #num_pic = cv2.imread('.\\'+dir+'\\' + i)
            num = int(num_pic[0][0:1])
            match_num(im, num_pic[1], num, result, 0, width)
    else:
        for num_pic in initThumbnail.bifen_new_right:
            #num_pic = cv2.imread('.\\'+dir+'\\' + i)
            num = int(num_pic[0][0:1])
            match_num(im, num_pic[1], num, result, 0, width)

    #cv2.imwrite("D:\\tuxiang\\tmp\\num.jpg",im)
    result.sort()
    result = list(i for i in result if i[0] < 0.3)
    for i in result:
        if i[1][0] > right_x:
            result_num += str(i[2])
            if len(result_num) == 1:
                left_x = i[1][0]
                right_x = left_x + width
            else:
                return int(result_num)
        elif i[1][0] < left_x - width:
            result_num = str(i[2]) + result_num
            return int(result_num)

    if len(result_num) <= 0:
        print("result score error")
        return "0"

    return result_num


#最终的数字
def ocr_small_num(frame,rect,width,leftOrRight):
    im=frame[rect[0]:rect[1],rect[2]:rect[3]]
    result = []
    result_num = ''
    left_x = 0
    right_x = 0
    if leftOrRight == "left":
        for num_pic in initThumbnail.bifen_new_left_small:
            #num_pic = cv2.imread('.\\'+dir+'\\' + i)
            num = int(num_pic[0][0:1])
            match_num(im, num_pic[1], num, result, 0, width)
    else:
        for num_pic in initThumbnail.bifen_new_right_small:
            #num_pic = cv2.imread('.\\'+dir+'\\' + i)
            num = int(num_pic[0][0:1])
            match_num(im, num_pic[1], num, result, 0, width)

    #cv2.imwrite("D:\\tuxiang\\tmp\\num.jpg",im)
    result.sort()
    result = list(i for i in result if i[0] < 0.3)
    for i in result:
        if i[1][0] > right_x:
            result_num += str(i[2])
            if len(result_num) == 1:
                left_x = i[1][0]
                right_x = left_x + width
            else:
                return int(result_num)
        elif i[1][0] < left_x - width:
            result_num = str(i[2]) + result_num
            return int(result_num)

    if len(result_num) <= 0:
        print("result score error")
        return "0"

    return result_num
