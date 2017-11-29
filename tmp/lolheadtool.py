import cv2
name = '16'

def cut():
    #while True:

    frame = cv2.imread("D:\\tuxiang\\tmp\\lolHeadRes\\{}.png".format(name))

    # 各种像素值
    #listY = [(143,207),(283,347),(423,487),(563,627)]
    listY = [(159, 223), (299, 363), (439, 503), (579, 643)]

    listX = [(283,347),(395,459),(507,571),(619,683),(731,795),(843,907),(955,1019)]


    index = 0
    for varX in listX:
        for varY in listY:
            saveFrame = frame[varY[0]:varY[1],varX[0]:varX[1]]
            cv2.imwrite("D:\\tuxiang\\tmp\\lolHeadRes\\{}_{}.png".format(name,index),saveFrame)
            index +=1

if __name__ == '__main__':
    cut()
