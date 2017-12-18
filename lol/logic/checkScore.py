
import cv2
#import pytesseract
import platform
import os
#from PIL import Image
from lol.logic import initThumbnail
from workerSvr.proc import procVariable



def checkScore(imCurrentFrame):

    dictRet = {}

    left_num = ocr_num(imCurrentFrame, initThumbnail.left_rentou, 15,"left")
    right_num = ocr_num(imCurrentFrame, initThumbnail.right_rentou, 15,"right")
    left_num_tower = ocr_small_num(imCurrentFrame, initThumbnail.left_tower, 10,"left")
    right_num_tower = ocr_small_num(imCurrentFrame, initThumbnail.right_tower, 10,"right")

    """
    if platform.system() == "Windows":
        if procVariable.debug:
            os.chdir('C:\Program Files (x86)\Tesseract-OCR')
        else:
            pass
        element = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

        config = "--psm 7 --oem 0 num"
        rect = initThumbnail.left_rentou
        left_num = test_ocr_2(imCurrentFrame, "D:/tmp/test6/leftkill.jpg", rect, config, element)

        rect = initThumbnail.right_rentou
        right_num = test_ocr(imCurrentFrame, "D:/tmp/test6/rightkill.jpg", rect, config, element)

        rect = initThumbnail.left_tower
        left_num_tower = test_ocr_2(imCurrentFrame, "D:/tmp/test6/lefttower.jpg", rect, config, element)

        rect = initThumbnail.right_tower
        right_num_tower = test_ocr(imCurrentFrame,"D:/tmp/test6/righttower.jpg",rect,config,element)

    else:
        pass
    """


    if left_num is not None and len(left_num):
        dictRet["leftKill"] = left_num
    if right_num is not None and len(right_num):
        dictRet["rightKill"] = right_num

    if left_num_tower is not None and len(left_num):
        dictRet["leftTower"] = left_num_tower

    if right_num_tower is not None and len(right_num_tower):
        dictRet["rightTower"] = right_num_tower

    return dictRet

def test_ocr(frame,write_path,rect,config,element):
    tempFrame = frame[rect[0]:rect[1], rect[2]:rect[3]]
    #tempFrame =  cv2.cvtColor(tempFrame,cv2.COLOR_RGBA2GRAY)
    #cv2.imshow("resultr", r)
    g,b,r = cv2.split(tempFrame)
    dilateFrame = cv2.dilate(r, element,borderType=cv2.BORDER_REFLECT)
    dilateFrame = cv2.erode(dilateFrame, element,iterations=5)
    img = Image.fromarray(dilateFrame)
    cv2.imwrite(write_path, dilateFrame)
    result = pytesseract.image_to_string(img, config=config)
    return result

def test_ocr_2(frame,write_path,rect,config,element):
    tempFrame = frame[rect[0]:rect[1], rect[2]:rect[3]]
    tempFrame =  cv2.cvtColor(tempFrame,cv2.COLOR_RGBA2GRAY)
    #cv2.imshow("resultr", r)
    #g,b,r = cv2.split(tempFrame)
    dilateFrame = cv2.dilate(tempFrame, element,borderType=cv2.BORDER_REFLECT)
    img = Image.fromarray(dilateFrame)
    cv2.imwrite(write_path, dilateFrame)
    result = pytesseract.image_to_string(img, config=config)
    return result

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
        match_num(im[:,res[2][0]+dis:], num_pic, num, result,x_s+res[2][0]+dis,dis)

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
                return result_num
        elif i[1][0] < left_x - width:
            result_num = str(i[2]) + result_num
            return result_num

    if len(result_num) <= 0:
        print("result score error")
        return

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
                return result_num
        elif i[1][0] < left_x - width:
            result_num = str(i[2]) + result_num
            return result_num

    if len(result_num) <= 0:
        print("result score error")
        return

    return result_num



if "__main__" == __name__:
    import pytesseract
    from PIL import Image
    import subprocess


    #frame = cv2.imread("D:\\tmp\\test6\\0039627.jpg",cv2.IMREAD_COLOR)
    #cv2.imwrite("D:\\tmp\\test6\\test_2.jpg",frame[19:67,  900: 942])
    #cv2.imwrite("D:\\tmp\\test6\\test_3.jpg", frame[19:67, 990: 1032])

    #src = cv2.imread("D:\\tmp\\test6\\test_2.jpg", cv2.IMREAD_GRAYSCALE)
    #cv2.imwrite("D:\\tmp\\test6\\test_4.jpg", src)

    #src = cv2.imread("D:\\tmp\\test6\\test_3.jpg", cv2.IMREAD_GRAYSCALE)
    #cv2.imwrite("D:\\tmp\\test6\\test_5.jpg", src)

    #cv2.dnn.blobFromImage()
    #img = Image.fromarray(src)
    #img.save()
    #num = pytesseract.image_to_string(Image.open("D:\\tmp\\test6\\test_5.jpg"))
    #print(num)

    #p = subprocess.Popen(["D:/tuxiang/lol/bifen_new_right/9.png", "stdout --psm 7 --oem 0 num"],executable="tesseract",stdout=subprocess.PIPE)
    #stdout = Popen("tesseract D:/tuxiang\lol/bifen_new_right/9.png stdout --psm 7 --oem 0 num")
    #print(stdout)
    #print(p.stdout.read())

    import os
    print(os.getcwd())
    os.chdir('C:\Program Files (x86)\Tesseract-OCR')
    src = cv2.imread("D:\\tmp\\test6\\8.jpg", cv2.IMREAD_GRAYSCALE)
    #img = Image.open("D:\\tmp\\test6\\8.jpg")
    print(os.getcwd())
    img = Image.fromarray(src)

    txt = pytesseract.image_to_string(img,config="--psm 7 --oem 0 num")
    print(txt)
    #cv2.imshow('image', src)
    k = cv2.waitKey(0)
    if k == 27:  # wait for ESC key to exit
        cv2.destroyAllWindows()
    elif k == ord('s'):  # wait for 's' key to save and exit
        cv2.destroyAllWindows()


