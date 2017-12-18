import cv2
import numpy as np
import time
import pickle
from ctypes import c_float,c_int,cast,POINTER
from lol.logic import initThumbnail
from workerSvr.singleton import singletonInstance
from learn import mnist_num
import copy

#提取所有的文字像素点
def word_extract(frame):
    im=np.zeros(frame.shape[:2]).astype(np.uint8)
    r=abs(frame[:,:,2].astype(np.int)-221)
    g=abs(frame[:,:,1].astype(np.int)-182)
    b=abs(frame[:,:,0].astype(np.int)-148)
    im[r+g+b<200]=1
    return im


def checkFighting(imCurrentFrame,indexFrame,strMatchType,strMatchId,iRound):

    retTenKillName = ""
    retDragonAttName = ""
    retListFirstTower = []
    retSmallDragon = ""
    retBigDragon = ""
    retFirstBlood = ""
    retXiaoGuXiangFeng = ""
    retFiveKill = ""
    retFourKill = ""
    retThreeKill = ""
    retGodLike = ""
    #intRealFrame = 0
    retDict = {}
    strShareKey = "{}{}_{}".format(strMatchType,strMatchId,iRound)

    fightingFrame = copy.deepcopy(imCurrentFrame[0:60, 856:856 + 222])
    fightingFrame[26:60-8, 48:48+43] = 0
    fightingFrame[25:60-6, 132:132+44] = 0

    res3 = cv2.matchTemplate(fightingFrame, initThumbnail.middle_black_head, cv2.TM_SQDIFF_NORMED)
    res3 = cv2.minMaxLoc(res3)[0]
    if res3 > 0.15:
        resReplay = cv2.matchTemplate(imCurrentFrame[120:170,0:200], initThumbnail.en_replay, cv2.TM_SQDIFF_NORMED)
        resReplay = cv2.minMaxLoc(resReplay)[0]
        if resReplay < 0.15:
            # 录像
            print("may be replay")
            retDict["replayFlag"] = True
            return retDict
        else:
            # 有可能比赛已经结束
            print("may be gameEnd")

            retDict["endGameFlag"] = True
            return retDict


    firstTenKillFrame = getTenKillFrame(strShareKey)
    firstDragonAttFrame = getFirstDragonAttFrame(strShareKey)#singletonInstance.first_dragon_attr_frame_proxy.get()
    temp_list = getCheckList(strShareKey)
    if firstTenKillFrame == 0:
        tenScoreCheckFrame = getTenCheckScoreAttFrame(strShareKey)
    else:
        #已经有10杀了,赋值0 就行了,下面用不到这个变量
        tenScoreCheckFrame = 0

    fim = word_extract(imCurrentFrame[220:275, 750:1325])
    for idx, i in enumerate(initThumbnail.en_all_pic_list):
        # 为了避免图像的像素点有偏移
        if i[1][0] < 5:
            y1 = 0
        else:
            y1 = i[1][0] - 5
        if i[1][2] < 5:
            x1 = 0
        else:
            x1 = i[1][2] - 5
        if i[1][1] > 1075:
            y2 = 1080
        else:
            y2 = i[1][1] + 5
        if i[1][3] > 1915:
            x2 = 1920
        else:
            x2 = i[1][3] + 5


        if not i[0] in initThumbnail.en_wordname_list:
            # 匹配红队，蓝队谁先10杀和第一条龙的信息
            if firstTenKillFrame == 0:
                if indexFrame > (tenScoreCheckFrame + 20):
                    # 检测率先10杀逻辑
                    if i[0] == "blue10.png":
                        firstNum = mnist_num.mnist_ocr_opencv(imCurrentFrame[25:52,990:1012],[35,39,10],"red")
                        cv2.imwrite("D:/mtest1.jpg",imCurrentFrame[25:52,990:1012])

                        secondNum = mnist_num.mnist_ocr_opencv(imCurrentFrame[25:52,1012:1034],[35,39,10],"red")
                        cv2.imwrite("D:/mtest2.jpg", imCurrentFrame[25:52,1012:1034])

                        if firstNum == 1 and secondNum == 0:
                            retTenKillName = 'blue'
                            setTenKillFrame(strShareKey, indexFrame)

                    elif i[0] == "red10.png":
                        firstNum = mnist_num.mnist_ocr_opencv(imCurrentFrame[25:52, 900:922],[35,39,10],"blue")
                        cv2.imwrite("D:/mtest3.jpg", imCurrentFrame[25:52, 900:922])

                        secondNum = mnist_num.mnist_ocr_opencv(imCurrentFrame[25:52, 922:942],[35,39,10],"blue")

                        cv2.imwrite("D:/mtest4.jpg", imCurrentFrame[25:52, 922:942])
                        if firstNum == 1 and secondNum == 0:
                            retTenKillName = 'red'
                            setTenKillFrame(strShareKey,indexFrame)

                        setTenCheckScoreFrame(strShareKey,indexFrame)

            pic = imCurrentFrame[y1:y2, x1:x2]
            #cv2.imwrite("D:/test.jpg",pic)
            pic1 = cv2.imread('../lol/pic_new/' + i[0], cv2.IMREAD_COLOR)
            res = cv2.matchTemplate(pic, pic1, cv2.TM_SQDIFF_NORMED)
            res = cv2.minMaxLoc(res)
            #all_result[idx].append((res[0], res[2]))
            '''
            if firstTenKillFrame == 0 and res[0] < 0.15 and i[0] in ('blue10.png', 'red10.png'):
                if i[0] == 'blue10.png':
                    retTenKillName = 'blue'
                else:
                    retTenKillName = 'red'

                setTenKillFrame(strShareKey,indexFrame)
                print("firsttenkill:" + retTenKillName)
            '''

            if firstDragonAttFrame == 0 and res[0] < 0.15 and \
                            i[0] in ('shuilong.png', 'huolong.png', 'tulong.png', 'yunlong.png', 'yuangulong.png'):
                setFirstDragonAttFrame(strShareKey, indexFrame)
                retDragonAttName = i[0][:i[0].index('.')]
                print("firstdragonatt:" + retDragonAttName)
        else:
            y1 -= 220
            y2 -= 220
            x1 -= 750
            x2 -= 750
            result = (c_float * 3)()
            im = fim[y1:y2, x1:x2]
            xx1 = im.shape[0]
            yy1 = im.shape[1]
            im = im.reshape(im.shape[0] * im.shape[1])
            i = initThumbnail.en_word_dic[i[0]]
            #s = time.clock()
            initThumbnail.matchtemplate(i[3], len(i[2]) // 2, i[4][0], i[4][1], cast(im.ctypes.data, POINTER(c_int)), xx1, yy1,
                          result)
            result = list(result)
            # 文字的位置
            r_x = int(result[2]) + 750 + x1
            r_y = int(result[1]) + 220 + y1
            #all_result[idx].append((1 - result[0], (r_x, r_y, np.average(im))))

            # 匹配上文字提示
            if 1 - result[0] < 0.25:
                # 上一帧也匹配上
                if r_x < temp_list[idx - 7][1]:
                    temp_list[idx - 7][1] = r_x
                if r_x > temp_list[idx - 7][2]:
                    temp_list[idx - 7][2] = r_x
                if r_y < temp_list[idx - 7][3]:
                    temp_list[idx - 7][3] = r_y
                if r_y > temp_list[idx - 7][4]:
                    temp_list[idx - 7][4] = r_y

                temp_list[idx - 7] = [indexFrame, r_x, r_x, r_y, r_y, None]

                """
                if temp_list[idx - 7][0] != -1:
                    if r_x < temp_list[idx - 7][1]:
                        temp_list[idx - 7][1] = r_x
                    if r_x > temp_list[idx - 7][2]:
                        temp_list[idx - 7][2] = r_x
                    if r_y < temp_list[idx - 7][3]:
                        temp_list[idx - 7][3] = r_y
                    if r_y > temp_list[idx - 7][4]:
                        temp_list[idx - 7][4] = r_y
                    # 连续匹配的文字坐标的坐标偏移不能超过2像素
                    if temp_list[idx - 7][4] - temp_list[idx - 7][3] > 2 or temp_list[idx - 7][2] - temp_list[idx - 7][
                        1] > 2:
                        temp_list[idx - 7] = [-1, 1920, 0, 1080, 0, None]
                else:
                    #temp_list[idx - 7] = [indexFrame, r_x, r_x, r_y, r_y, None]
                    #setCheckList(strShareKey, temp_list)
                # 匹配上后的第20帧取出来用来匹配英雄
                #if indexFrame - temp_list[idx - 7][0] == 20:
                    #temp_list[idx - 7][-1] = imCurrentFrame
                    #setCheckList(strShareKey, temp_list)
                """
                # 一塔
                if idx == 14:
                    # temp_y = (temp_list[7][3] + temp_list[7][4]) // 2
                    # temp_x = (temp_list[7][1] + temp_list[7][2]) // 2
                    # im = word_extract(lastFrame[temp_y:temp_y + 37, temp_x - 167:temp_x - 115])
                    # result = (c_float * 3)()
                    # xx1 = im.shape[0]
                    # yy1 = im.shape[1]
                    # im = im.reshape(im.shape[0] * im.shape[1])
                    # 判断是红队一塔还是蓝队一塔
                    # i = initThumbnail.en_yita_list[0]
                    # initThumbnail.matchtemplate(i[3], len(i[2]) // 2, i[4][0], i[4][1], cast(im.ctypes.data, POINTER(c_int)), xx1,
                    #              yy1, result)
                    # r_blue = result[0]
                    # i = initThumbnail.en_yita_list[1]
                    # initThumbnail.matchtemplate(i[3], len(i[2]) // 2, i[4][0], i[4][1], cast(im.ctypes.data, POINTER(c_int)), xx1,
                    #              yy1, result)
                    # r_red = result[0]
                    tem = match_heroes(imCurrentFrame[210:275, 588:669], initThumbnail.heroes_55, False)
                    # print("xxxxxxxxxx[{}]  [{}]".format(r_blue,r_red))
                    # if r_blue > r_red:
                    # final_result[-1].append((temp_list[7][0], 'blue', tem[0]))
                    #    print("bluetower" + str(tem[0]))
                    #    retListFirstTower = ['blue', tem[0]]
                    # else:
                    # final_result[-1].append((temp_list[7][0], 'red', tem[0]))
                    #    print("redtower" + str(tem[0]))
                    #    retListFirstTower = ['red',tem[0]]
                    print("firsttower " + tem[0])
                    retListFirstTower = tem[0]

                # 峡谷先锋
                elif idx == 11:
                    # temp_y = (temp_list[idx - 7][3] + temp_list[idx - 7][4]) // 2
                    temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                    tem = match_heroes(imCurrentFrame[210:275, temp_x - 240:temp_x - 164], initThumbnail.heroes_55, False)
                    # final_result[idx - 5].append((temp_list[idx - 7][0], tem[0]))
                    print("xianguxianfeng " + tem[0])
                    retXiaoGuXiangFeng = tem[0]
                # 小龙
                elif idx == 12:
                    # temp_y = (temp_list[idx - 7][3] + temp_list[idx - 7][4]) // 2
                    temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                    tem = match_heroes(imCurrentFrame[210:275, temp_x - 240:temp_x - 164], initThumbnail.heroes_55, False)
                    cv2.imwrite("D:/test.jpg",imCurrentFrame[210:275, temp_x - 240:temp_x - 164])
                    # final_result[idx - 5].append((temp_list[idx - 7][0], tem[0]))
                    print("smallDragon " + tem[0])
                    retSmallDragon = tem[0]
                # 纳什男爵
                elif idx == 13:
                    # temp_y = (temp_list[idx - 7][3] + temp_list[idx - 7][4]) // 2
                    temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                    tem = match_heroes(imCurrentFrame[210:275, temp_x - 240:temp_x - 164], initThumbnail.heroes_55, False)
                    # final_result[idx - 5].append((temp_list[idx - 7][0], tem[0]))
                    print("bigDragon " + tem[0])
                    retBigDragon = tem[0]

                # 一血，匹配英雄头像
                elif idx == 9:
                    tem = match_heroes(imCurrentFrame[139:214, 923:998], initThumbnail.heroes_55, False)
                    # final_result[idx - 5].append((temp_list[idx - 7][0], tem[0]))
                    print("firstblood " + tem[0])
                    retFirstBlood = tem[0]
                elif idx == 8:
                    tem = match_heroes(imCurrentFrame[128:213, 917:1002], initThumbnail.heroes_65, False)
                    print("fourkill:" + str(tem[0]))
                    retFiveKill = str(tem[0])
                elif idx == 10:
                    # 超神
                    # temp_y = (temp_list[idx - 7][3] + temp_list[idx - 7][4]) // 2
                    # temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                    # temp_x_right = temp_x + i[4][1]
                    x_left = 405
                    # x_right = temp_x + initThumbnail.en_hero_word_x_diff[idx - 7][1]
                    tem_l = match_heroes(imCurrentFrame[210:275, x_left - 5:x_left + 60], initThumbnail.heroes_55, False)
                    # tem_r = match_heroes(lastFrame[210:275, x_right - 5:x_right + 60], initThumbnail.heroes_55, False)
                    retGodLike = tem_l[0]
                    print("godlike " + retGodLike)
                elif idx == 8:
                    # 四杀
                    # temp_y = (temp_list[idx - 7][3] + temp_list[idx - 7][4]) // 2
                    temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                    # temp_x_right = temp_x + i[4][1]

                    x_left = temp_x - initThumbnail.en_hero_word_x_diff[idx - 7][0]
                    # x_right = temp_x + initThumbnail.en_hero_word_x_diff[idx - 7][1]
                    tem_l = match_heroes(imCurrentFrame[210:275, x_left - 5:x_left + 60], initThumbnail.heroes_55, False)
                    # tem_r = match_heroes(lastFrame[210:275, x_right - 5:x_right + 60], initThumbnail.heroes_55,
                    #                     False)
                    retFourKill = tem_l[0]
                    print("four kill " + retGodLike)

                elif idx == 7:
                    # 三杀
                    temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2

                    x_left = temp_x - initThumbnail.en_hero_word_x_diff[idx - 7][0]
                    # x_right = temp_x + initThumbnail.en_hero_word_x_diff[idx - 7][1]
                    tem_l = match_heroes(imCurrentFrame[210:275, x_left - 5:x_left + 60], initThumbnail.heroes_55, False)
                    retThreeKill = tem_l[0]
                    print("three kill " + retGodLike)
                elif idx == 15:
                    # 5杀
                    # temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                    # x_left = temp_x - initThumbnail.en_hero_word_x_diff[idx - 7][0]
                    # x_right = temp_x + initThumbnail.en_hero_word_x_diff[idx - 7][1]
                    try:
                        tem_l = match_heroes(imCurrentFrame[222:270, 796:796 + 336], initThumbnail.heroes_55, False)
                        retFiveKill = tem_l[0]
                        print("five kill " + tem_l[0])
                    except Exception as e:
                        print(repr(e))

                else:
                    pass

            """
            else:
                # 连续20帧匹配上
                if temp_list[idx - 7][0] != -1 and indexFrame - temp_list[idx - 7][0] > 20:
                    lastFrame = temp_list[idx - 7][-1]
                    intRealFrame = temp_list[idx - 7][0]
                    #cv2.imwrite('../snap/' + str(indexFrame) + '_' + str(idx) + '.png', saveFrame)
                    #print(temp_list[idx - 7][:-1])
                    # 一塔
                    if idx == 14:
                        #temp_y = (temp_list[7][3] + temp_list[7][4]) // 2
                        #temp_x = (temp_list[7][1] + temp_list[7][2]) // 2
                        #im = word_extract(lastFrame[temp_y:temp_y + 37, temp_x - 167:temp_x - 115])
                        #result = (c_float * 3)()
                        #xx1 = im.shape[0]
                        #yy1 = im.shape[1]
                        #im = im.reshape(im.shape[0] * im.shape[1])
                        # 判断是红队一塔还是蓝队一塔
                        #i = initThumbnail.en_yita_list[0]
                        #initThumbnail.matchtemplate(i[3], len(i[2]) // 2, i[4][0], i[4][1], cast(im.ctypes.data, POINTER(c_int)), xx1,
                        #              yy1, result)
                        #r_blue = result[0]
                        #i = initThumbnail.en_yita_list[1]
                        #initThumbnail.matchtemplate(i[3], len(i[2]) // 2, i[4][0], i[4][1], cast(im.ctypes.data, POINTER(c_int)), xx1,
                        #              yy1, result)
                        #r_red = result[0]
                        tem = match_heroes(lastFrame[210:275, 588:669], initThumbnail.heroes_55, False)
                        #print("xxxxxxxxxx[{}]  [{}]".format(r_blue,r_red))
                        #if r_blue > r_red:
                            #final_result[-1].append((temp_list[7][0], 'blue', tem[0]))
                        #    print("bluetower" + str(tem[0]))
                        #    retListFirstTower = ['blue', tem[0]]
                        #else:
                            #final_result[-1].append((temp_list[7][0], 'red', tem[0]))
                        #    print("redtower" + str(tem[0]))
                        #    retListFirstTower = ['red',tem[0]]
                        print("firsttower " + tem[0])
                        retListFirstTower = tem[0]

                    # 峡谷先锋
                    elif idx == 11:
                        #temp_y = (temp_list[idx - 7][3] + temp_list[idx - 7][4]) // 2
                        temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                        tem = match_heroes(lastFrame[210:275, temp_x - 240:temp_x - 164], initThumbnail.heroes_55, False)
                        #final_result[idx - 5].append((temp_list[idx - 7][0], tem[0]))
                        print("xianguxianfeng " + tem[0])
                        retXiaoGuXiangFeng = tem[0]
                    # 小龙
                    elif idx == 12:
                        #temp_y = (temp_list[idx - 7][3] + temp_list[idx - 7][4]) // 2
                        temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                        tem = match_heroes(lastFrame[210:275, temp_x - 240:temp_x - 164], initThumbnail.heroes_55, False)
                        #final_result[idx - 5].append((temp_list[idx - 7][0], tem[0]))
                        print("smallDragon " + tem[0])
                        retSmallDragon = tem[0]
                    # 纳什男爵
                    elif idx == 13:
                        #temp_y = (temp_list[idx - 7][3] + temp_list[idx - 7][4]) // 2
                        temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                        tem = match_heroes(lastFrame[210:275, temp_x - 240:temp_x - 164], initThumbnail.heroes_55, False)
                        #final_result[idx - 5].append((temp_list[idx - 7][0], tem[0]))
                        print("bigDragon " + tem[0])
                        retBigDragon = tem[0]

                    # 一血，匹配英雄头像
                    elif idx == 9:
                        tem = match_heroes(lastFrame[139:214, 923:998], initThumbnail.heroes_55, False)
                        #final_result[idx - 5].append((temp_list[idx - 7][0], tem[0]))
                        print("firstblood " + tem[0])
                        retFirstBlood = tem[0]
                    elif idx == 8:
                        tem = match_heroes(lastFrame[128:213, 917:1002], initThumbnail.heroes_65, False)
                        print("fourkill:" + str(tem[0]))
                        retFiveKill = str(tem[0])
                    elif idx == 10:
                        #超神
                        #temp_y = (temp_list[idx - 7][3] + temp_list[idx - 7][4]) // 2
                        #temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                        #temp_x_right = temp_x + i[4][1]
                        x_left = 405
                        #x_right = temp_x + initThumbnail.en_hero_word_x_diff[idx - 7][1]
                        tem_l = match_heroes(lastFrame[210:275, x_left - 5:x_left + 60], initThumbnail.heroes_55, False)
                        #tem_r = match_heroes(lastFrame[210:275, x_right - 5:x_right + 60], initThumbnail.heroes_55, False)
                        retGodLike = tem_l[0]
                        print("godlike " + retGodLike)
                    elif idx == 8:
                        #四杀
                        #temp_y = (temp_list[idx - 7][3] + temp_list[idx - 7][4]) // 2
                        temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                        #temp_x_right = temp_x + i[4][1]

                        x_left = temp_x - initThumbnail.en_hero_word_x_diff[idx - 7][0]
                        #x_right = temp_x + initThumbnail.en_hero_word_x_diff[idx - 7][1]
                        tem_l = match_heroes(lastFrame[210:275, x_left - 5:x_left + 60], initThumbnail.heroes_55, False)
                        #tem_r = match_heroes(lastFrame[210:275, x_right - 5:x_right + 60], initThumbnail.heroes_55,
                        #                     False)
                        retFourKill = tem_l[0]
                        print("four kill " + retGodLike)

                    elif idx == 7:
                        # 三杀
                        temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2

                        x_left = temp_x - initThumbnail.en_hero_word_x_diff[idx - 7][0]
                        #x_right = temp_x + initThumbnail.en_hero_word_x_diff[idx - 7][1]
                        tem_l = match_heroes(lastFrame[210:275, x_left - 5:x_left + 60], initThumbnail.heroes_55, False)
                        retThreeKill = tem_l[0]
                        print("three kill " + retGodLike)
                    elif idx == 15:
                        # 5杀
                        #temp_x = (temp_list[idx - 7][1] + temp_list[idx - 7][2]) // 2
                        #x_left = temp_x - initThumbnail.en_hero_word_x_diff[idx - 7][0]
                        #x_right = temp_x + initThumbnail.en_hero_word_x_diff[idx - 7][1]
                        try:
                            tem_l = match_heroes(lastFrame[222:270, 796:796+336], initThumbnail.heroes_55, False)
                            retFiveKill = tem_l[0]
                            print("five kill " + tem_l[0])
                        except Exception as e:
                            print(repr(e))

                    else:
                        pass
                    #print(final_result)
                if temp_list[idx - 7][0] != -1:
                    temp_list[idx - 7] = [-1, 1920, 0, 1080, 0, None]
                    setCheckList(strShareKey, temp_list)
            """

    retDict = {}
    if len(retTenKillName) != 0:
        retDict["retTenKillName"] = retTenKillName
    if len(retDragonAttName) != 0:
        retDict["retDragonAttName"] = retDragonAttName

    if len(retListFirstTower) != 0:
        retDict["retListFirstTower"] = retListFirstTower

    if len(retXiaoGuXiangFeng) != 0:
        retDict["retXiaoGuXiangFeng"] = retXiaoGuXiangFeng

    if len(retSmallDragon) != 0:
        retDict["retSmallDragon"] = retSmallDragon

    if len(retBigDragon) != 0:
        retDict["retBigDragon"] = retBigDragon

    if len(retFirstBlood) != 0:
        retDict["retFirstBlood"] = retFirstBlood

    if len(retThreeKill) != 0:
        retDict["retThreeKill"] = retThreeKill

    if len(retFourKill) != 0:
        retDict["retFourKill"] = retFourKill

    if len(retFiveKill) != 0:
        retDict["retFiveKill"] = retFiveKill

    if len(retGodLike) != 0:
        retDict["retGodLike"] = retGodLike

    #TODO 以后改到 task 里面去读，不要放到具体逻辑里面

    #这里的帧数,因为匹配的那个帧是发现后20帧，然后发现后的大于50帧开始进行匹配返回结果
    retDict["realFrameIndex"] = indexFrame
    retDict["frameIndex"] = indexFrame
    #return retTenKillName,retDragonAttName,retListFirstTower,retXiaoGuXiangFeng,retFirstSmallDragon,retFirstBigDragon,retFirstBlood
    return retDict

# 匹配英雄
def match_heroes(frame, heroes, flag):
    # 背景置为黑色
    if flag:
        radius = (frame.shape[0] - 1) // 2
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                if (i - radius) ** 2 + (j - radius) ** 2 > radius * radius:
                    frame[i, j] = 0

    t = []
    for idx, hero in enumerate(heroes):
        res = cv2.matchTemplate(frame, hero[0], cv2.TM_CCOEFF_NORMED)
        res = cv2.minMaxLoc(res)
        t.append((res[1], hero[1]))
    t.sort()
    t = t[::-1]
    return (t[0][1], t[0][0])

def getTenKillFrame(shareKey:str):
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)

    return dictShareMatchData["first_ten_kill_frame_proxy"]

def getFirstDragonAttFrame(shareKey:str):
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)

    return dictShareMatchData["first_dragon_attr_frame_proxy"]

def getTenCheckScoreAttFrame(shareKey:str):
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)

    return dictShareMatchData["ten_check_score_frame_proxy"]


def getCheckList(shareKey:str):
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)

    return dictShareMatchData["check_list"]


def setTenKillFrame(shareKey:str,tt:int):
    #singletonInstance.first_ten_kill_frame_proxy.set(tt)
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)
    dictShareMatchData["first_ten_kill_frame_proxy"] = tt
    bytesShareMatchData = pickle.dumps(dictShareMatchData)
    singletonInstance.share_dict[shareKey] = bytesShareMatchData

    print("set ten kill tt[{}]".format(tt))

def setFirstDragonAttFrame(shareKey:str,tt:int):
    #singletonInstance.first_dragon_attr_frame_proxy.set(tt)
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)
    dictShareMatchData["first_dragon_attr_frame_proxy"] = tt
    bytesShareMatchData = pickle.dumps(dictShareMatchData)
    singletonInstance.share_dict[shareKey] = bytesShareMatchData

    print("set first dragon tt[{}]".format(tt))


def setTenCheckScoreFrame(shareKey:str,tt:int):
    #singletonInstance.first_dragon_attr_frame_proxy.set(tt)
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)
    dictShareMatchData["ten_check_score_frame_proxy"] = tt
    bytesShareMatchData = pickle.dumps(dictShareMatchData)
    singletonInstance.share_dict[shareKey] = bytesShareMatchData

    print("set ten check score tt[{}]".format(tt))


def setCheckList(shareKey:str,check:list):
    #singletonInstance.first_dragon_attr_frame_proxy.set(tt)
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)
    dictShareMatchData["check_list"] = check
    bytesShareMatchData = pickle.dumps(dictShareMatchData)
    singletonInstance.share_dict[shareKey] = bytesShareMatchData

    #print("set check list tt[{}]".format(check))
