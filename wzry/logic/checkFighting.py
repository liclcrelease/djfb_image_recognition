import cv2
import pickle
from wzry.logic import initThumbnail
from workerSvr.singleton import singletonInstance
#from wzry.logic import checkBegin

def checkLeftFighting(imCurrentFrame):
    #l_s = imCurrentFrame[9:54, 451:496]
    #r_s = imCurrentFrame[9:54, 720:765]

    #l_s_small = imCurrentFrame[215:251, 684:720]
    #r_s_small = imCurrentFrame[215:251, 869:905]


    #res1 = cv2.matchTemplate(l_s, initThumbnail.sPic, cv2.TM_SQDIFF_NORMED)
    #res1 = cv2.minMaxLoc(res1)[0]
    #res2 = cv2.matchTemplate(l_s, initThumbnail.sPic, cv2.TM_SQDIFF_NORMED)
    #res2 = cv2.minMaxLoc(res2)[0]
    #res3 = cv2.matchTemplate(l_s, initThumbnail.s_smallPic, cv2.TM_SQDIFF_NORMED)
    #res3 = cv2.minMaxLoc(res3)[0]
    #res4 = cv2.matchTemplate(l_s, initThumbnail.s_smallPic, cv2.TM_SQDIFF_NORMED)
    #res4 = cv2.minMaxLoc(res4)[0]
    # 匹配到白框
    #if res1+res2 < 0.01 or res3+res4<0.01:
    #    return True

    rpic1 = imCurrentFrame[0:93, 343:430]
    for i in range(355, 391):
        for j in range(22, 77):
            imCurrentFrame[j, i] = 0

    res = cv2.matchTemplate(rpic1, initThumbnail.leftPic, cv2.TM_SQDIFF_NORMED)[0][0]
    if res < 0.01:
        return True

    return False

def checkFighting(imCurrentFrame,indexFrame,strMatchType,strMatchId,iRound):


    listJiSha = []
    #jisha_type = 0
    retDict = {}
    strShareKey = "{}{}_{}".format(strMatchType, strMatchId, iRound)


    if not checkLeftFighting(imCurrentFrame):
        # 有可能比赛已经结束
        retDict["endGameFlag"] = True
        return retDict

    jishTT = getIndexJiShaFrame(strShareKey)
    jisha_type = getJiShaType(strShareKey)
    #print("jisha [{}]".format(jishTT))

    #with singletonInstance.kill_frame.get_lock():
    #    tt = singletonInstance.kill_frame

    for idx,jisha_t in enumerate(initThumbnail.jisha):
        #截取矩形框
        temp=imCurrentFrame[jisha_t[2][1]:jisha_t[2][3],jisha_t[2][0]:jisha_t[2][2]]
        #匹配值越小越相似
        #print("ppppppppppppppppp")
        #try:
        res=cv2.matchTemplate(temp,jisha_t[0],cv2.TM_SQDIFF_NORMED)[0][0]
        #except:
        #    print("xxx")
        #阈值设置为0.15
        #print(res)
        if res<0.2:
            print("yyyyyyyyyyyyyyyyyyyy cache")
            '''
            #用百度api识别比分，判断是否是回放，暂时注掉，一场比赛大概用api2000次左右

            cv2.imwrite('temp_baidu.jpg',frame[34:76,988:1041])
            temp_im=Image.open('temp_baidu.jpg').filter(ImageFilter.SHARPEN)
            temp_im.save('temp_baidu.jpg')
            result1 = ocr.ocr('temp_baidu.jpg')

            cv2.imwrite('temp_baidu.jpg',frame[34:76,881:941])
            temp_im=Image.open('temp_baidu.jpg').filter(ImageFilter.SHARPEN)
            temp_im.save('temp_baidu.jpg')
            result2 = ocr.ocr('temp_baidu.jpg')

            if 'words_result_num' not in result1:
                cv2.imwrite('error.png', frame)
            else:
                if result1['words_result_num']!=1:
                    result1=bifen1
                else:
                    result1=int(result1['words_result'][0]['words'])

            if 'words_result_num' not in result2:
                cv2.imwrite('error.png', frame)
            else:
                if result2['words_result_num']!=1:
                    result2=bifen2
                else:
                    result2=int(result2['words_result'][0]['words'])

            if result1<bifen1 or result2<bifen2:
                huifang=True
            else:
                huifang=False
                bifen1,bifen2=result1,result2
            '''

            # tt为上一次击杀暴君的帧数，i是现在的帧数，i-tt大于100判断为不同的击杀信息
            if not jishTT or indexFrame - jishTT > 100:

                setIndexJiShaFrame(strShareKey,indexFrame)
                jishTT = indexFrame

                #tt = indexFrame
                if jisha_t[1] == 'jisha.png':
                    #jisha_type = 1
                    setJiShaType(strShareKey,1)
                else:
                    setJiShaType(strShareKey, 2)
                    #jisha_type = 2
            elif jisha_type == 1:
                # 击败：出现击败文字后第12帧头像位置固定并且无遮挡，用来识别
                if indexFrame - jishTT == 12:
                    # 击杀者，背景置为黑色
                    yingxiong = imCurrentFrame[174:248, 738:837]
                    for i1 in range(74):
                        for j1 in range(99):
                            if (i1 - 49) ** 2 + (j1 - 49) ** 2 > 49 * 49:
                                yingxiong[i1, j1] = 0
                    # 被击杀者，背景置为黑色
                    yingxiong1 = imCurrentFrame[174:248, 1107:1206]
                    for i1 in range(74):
                        for j1 in range(99):
                            if (i1 - 49) ** 2 + (j1 - 49) ** 2 > 49 * 49:
                                yingxiong1[i1, j1] = 0
                    # [击杀者，击杀类别，被击杀者，出现击杀信息的帧数]
                    # result.append([match_heroes(yingxiong),jisha_t[1],match_heroes(yingxiong1),tt])
                    listJiSha.append([match_heroes(yingxiong), jisha_t[1], match_heroes(yingxiong1), jishTT, False])

            else:
                # 其他击杀类别：出现击败文字后第4帧头像位置固定并且无遮挡，用来识别
                print("xxxxxxxxxxxx [{}]".format(indexFrame - jishTT))
                if (indexFrame - jishTT) >= 4 and (indexFrame - jishTT <= 10):
                    # 同上
                    yingxiong = imCurrentFrame[174:248, 721:820]
                    for i1 in range(74):
                        for j1 in range(99):
                            if (i1 - 49) ** 2 + (j1 - 49) ** 2 > 49 * 49:
                                yingxiong[i1, j1] = 0
                    yingxiong1 = imCurrentFrame[174:248, 1137:1236]
                    for i1 in range(74):
                        for j1 in range(99):
                            if (i1 - 49) ** 2 + (j1 - 49) ** 2 > 49 * 49:
                                yingxiong1[i1, j1] = 0
                    # result.append([match_heroes(yingxiong),jisha_t[1],match_heroes(yingxiong1),tt])
                    listJiSha.append([match_heroes(yingxiong), jisha_t[1], match_heroes(yingxiong1), jishTT])

    #if len(listJiSha) > 0:
    #    print(listJiSha)

    fps = 25
    listTuiTa = []
    tuitaTT = getIndexTowerFrame(strShareKey)
    #print("tuita [{}]".format(tuitaTT))

    temp = imCurrentFrame[200:253, 897:1048]
    res = cv2.matchTemplate(temp, initThumbnail.diFang, cv2.TM_SQDIFF_NORMED)[0][0]
    temp = imCurrentFrame[200:253, 871:1022]
    res1 = cv2.matchTemplate(temp, initThumbnail.woFang, cv2.TM_SQDIFF_NORMED)[0][0]

    if res1 < 0.2 or res < 0.2:

        if not tuitaTT or indexFrame - tuitaTT > 100:
            setIndexTowerFrame(strShareKey,indexFrame)
            tuitaTT = indexFrame

        elif indexFrame - tuitaTT == 4:
            if res < 0.2:
                print(str(int(indexFrame / fps / 60)).zfill(2) + ':' + str(indexFrame / fps - int(indexFrame / fps / 60) * 60)[:5],
                      'cuihuidifangfangyuta')

            if res1 < 0.2:
                print(str(int(indexFrame / fps / 60)).zfill(2) + ':' + str(indexFrame / fps - int(indexFrame / fps / 60) * 60)[:5],
                      'wofangfangyutabeicuihui')
            yingxiong = imCurrentFrame[174:248, 643:742]

            for i1 in range(74):
                for j1 in range(99):
                    if (i1 - 49) ** 2 + (j1 - 49) ** 2 > 49 * 49:
                        yingxiong[i1, j1] = 0
            #print('yingxiong:', match_heroes(yingxiong))

            listTuiTa.append([match_heroes(yingxiong),indexFrame])
            #print(listTuiTa)

    listLong = []
    dragonTT = getIndexDragonFrame(strShareKey)
    #print("dragonTT [{}]".format(dragonTT))

    # 和三个文字信息分别进行匹配，匹配值越小越相似
    temp = imCurrentFrame[196:253, 818:1023]
    res = cv2.matchTemplate(temp, initThumbnail.baojun, cv2.TM_SQDIFF_NORMED)[0][0]
    res1 = cv2.matchTemplate(temp, initThumbnail.zhuzai, cv2.TM_SQDIFF_NORMED)[0][0]
    res2 = cv2.matchTemplate(imCurrentFrame[196:253, 871:1073], initThumbnail.heianbaojun, cv2.TM_SQDIFF_NORMED)[0][0]

    # 阈值设置为0.1
    if res < 0.1 or res1 < 0.1 or res2 < 0.1:
        # tt为上一次击杀暴君的帧数，i是现在的帧数，i-tt大于100判断为不同的击杀暴君信息
        if not dragonTT or indexFrame - dragonTT > 100:
            setIndexDragonFrame(strShareKey,indexFrame)
            dragonTT = indexFrame

        # 出现暴君信息后第4帧匹配头像（防止刚出现时头像有变形）
        elif (indexFrame - dragonTT >= 4) and (indexFrame - dragonTT <= 8):
            '''
            if res < 0.1:
                print(str(int(i / 25 / 60)).zfill(2) + ':' + str(i / 25 - int(i / 25 / 60) * 60)[:5], 'baojun')
            elif res1 < 0.1:
                print(str(int(i / 25 / 60)).zfill(2) + ':' + str(i / 25 - int(i / 25 / 60) * 60)[:5], 'zhuzai')
            else:
                print(str(int(i / 25 / 60)).zfill(2) + ':' + str(i / 25 - int(i / 25 / 60) * 60)[:5], 'heianbaojun')
            '''

            # 暴君，主宰和黑暗暴君的英雄头像位置不同
            if res < 0.1:
                yingxiong = imCurrentFrame[174:248, 674:773]
                type = "baojun"
            elif res1 < 0.1:
                yingxiong = imCurrentFrame[174:248, 674:773]
                type = "zhuzai"
            else:
                yingxiong = imCurrentFrame[174:248, 635:734]
                type = "heianbaojun"
            # 英雄头像背景变为黑色
            for i1 in range(74):
                for j1 in range(99):
                    if (i1 - 49) ** 2 + (j1 - 49) ** 2 > 49 * 49:
                        yingxiong[i1, j1] = 0

            listLong.append([match_heroes(yingxiong),type,indexFrame])
            #print(listLong)

    #return listJiSha,listTuiTa,listLong
    #retDict = {}
    retDict["listJiSha"] = listJiSha
    retDict["listTuiTa"] = listTuiTa
    retDict["listLong"] = listLong

    return retDict


# 匹配击杀英雄
def match_heroes(frame):
    t = []
    for idx, hero in enumerate(initThumbnail.jishaheroes):
        # res值越大匹配程度越高
        res = cv2.matchTemplate(frame, hero[0], cv2.TM_CCOEFF_NORMED)[0][0]
        t.append((res, hero[1]))

    t.sort()
    t = t[::-1]
    return t[0][1]



def getJiShaType(shareKey:str):
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)
    return dictShareMatchData["jisha_type"]


def getIndexJiShaFrame(shareKey:str):
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)
    return dictShareMatchData["kill_frame_proxy"]


def getIndexTowerFrame(shareKey:str):
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)

    return dictShareMatchData["kill_tower_frame_proxy"]

def getIndexDragonFrame(shareKey:str):
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)

    return dictShareMatchData["kill_dragon_frame_proxy"]


def setIndexJiShaFrame(shareKey:str,tt:int):

    '''
    if singletonInstance.task_condition.acquire():
        singletonInstance.objShareMgr.get_kill_frame().set(tt)
        #print(tt)
        singletonInstance.task_condition.notify()
        singletonInstance.task_condition.release()
    else:
        singletonInstance.task_condition.wait()

    return tt
    '''
    #with singletonInstance.kill_frame_proxy.get_lock():
    #singletonInstance.kill_frame_proxy.set(tt)
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)
    dictShareMatchData["kill_frame_proxy"] = tt
    bytesShareMatchData = pickle.dumps(dictShareMatchData)
    singletonInstance.share_dict[shareKey] = bytesShareMatchData
    print("set jisha kill tt[{}]".format(tt))


def setIndexTowerFrame(shareKey:str,tt:int):
    #with singletonInstance.kill_frame_proxy.get_lock():
    #singletonInstance.kill_tower_frame_proxy.set(tt)
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)
    dictShareMatchData["kill_tower_frame_proxy"] = tt
    bytesShareMatchData = pickle.dumps(dictShareMatchData)
    singletonInstance.share_dict[shareKey] = bytesShareMatchData

    #singletonInstance.share_dict[shareKey]["kill_tower_frame_proxy"] = tt
    print("set tower kill tt[{}]".format(tt))


def setIndexDragonFrame(shareKey:str,tt:int):
    #with singletonInstance.kill_frame_proxy.get_lock():
    #singletonInstance.kill_dragon_frame_proxy.set(tt)
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)
    dictShareMatchData["kill_dragon_frame_proxy"] = tt
    bytesShareMatchData = pickle.dumps(dictShareMatchData)
    singletonInstance.share_dict[shareKey] = bytesShareMatchData

    #singletonInstance.share_dict[shareKey]["kill_dragon_frame_proxy"] = tt
    print("set dragon kill tt[{}]".format(tt))

def setJiShaType(shareKey:str,type:int):
    #with singletonInstance.kill_frame_proxy.get_lock():
    #singletonInstance.kill_dragon_frame_proxy.set(tt)
    bytesShareMatchData = singletonInstance.share_dict[shareKey]
    dictShareMatchData = pickle.loads(bytesShareMatchData)
    dictShareMatchData["jisha_type"] = type
    bytesShareMatchData = pickle.dumps(dictShareMatchData)
    singletonInstance.share_dict[shareKey] = bytesShareMatchData

    #singletonInstance.share_dict[shareKey]["kill_dragon_frame_proxy"] = tt
    print("set jisha kill type [{}]".format(type))