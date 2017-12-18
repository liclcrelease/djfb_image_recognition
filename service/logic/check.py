from service.singleton import singletonInstance
from service import serviceConfig
from service.logic import post
from lib.timehelp import timeHelp
from lol.heroConfig import HeroConfig_cfg as lolHeroConfig
from wzry.heroConfig import HeroConfig_cfg as wzryHeroConfig
import pickle
import json
import time
import logging

def checkResult():

    while True:

        # 验证返回结果
        if True:
            if not singletonInstance.result_queue.empty():
                bytesResult = singletonInstance.result_queue.get()

                objResult = pickle.loads(bytesResult)

                strShareKey = "{}{}_{}".format(objResult.strMatchType, objResult.strMatchId, objResult.iRound)
                objMatchData = singletonInstance.g_matchData.get(strShareKey,None)

                if objMatchData is None:
                    logging.debug("error match data is None")
                    continue

                '''
                if objMatchData.getCloseImageCheck():
                    print("match image check end")
                    return
                '''
                # lol,wzry 的结果
                if objResult.result == "beginGame":
                    intCheckNum = objMatchData.addBeginCheckNum()
                    if intCheckNum > 5:
                        #超过5帧的比赛开始的统计
                        objMatchData.setGameState("chooseHero")
                # lol,wzry 的结果
                elif objResult.result == "endChoose":
                    listTotalTeam = pickle.loads(objResult.value)
                    logging.debug(listTotalTeam)
                    #TODO 可以查看到返回值和当前队伍的队员是否一致,需要计算队员
                    if objResult.strMatchType == "lol":
                        for var in listTotalTeam[0:5]:
                            if var[0] > 0.15:
                                logging.debug("blue team {} {} may be wrong".format(lolHeroConfig[var[2][:-4]],var[0]))
                            else:
                                #print("{} {} may be wrong".format(var[0], HeroConfig_cfg[var[2][:-4]]))
                                logging.debug("blue team {}".format(lolHeroConfig[var[2][:-4]]))

                            objMatchData.arrayBlueTeam.append(var[2])
                        for var in listTotalTeam[5:10]:
                            if var[0] > 0.15:
                                logging.debug("red team {} {} may be wrong".format(lolHeroConfig[var[2][:-4]],var[0]))
                            else:
                                logging.debug("red team {}".format(lolHeroConfig[var[2][:-4]]))

                            objMatchData.arrayRedTeam.append(var[2])

                    else:
                        objMatchData.arrayBlueTeam = listTotalTeam[0:5]
                        objMatchData.arrayRedTeam = listTotalTeam[5:10]

                        for var in objMatchData.arrayBlueTeam:
                            logging.debug("blue team {}".format(wzryHeroConfig[var.split(".")[0][5:]]["hero_name"]))
                        for var in objMatchData.arrayRedTeam:
                            logging.debug("red team {}".format(wzryHeroConfig[var.split(".")[0][5:]]["hero_name"]))

                    objMatchData.setGameState("fighting")

                # wzry 的结果
                elif objResult.result == "jisha":
                    dictJiSha = pickle.loads(objResult.value)
                    strPlayType = dictJiSha["des"]

                    if strPlayType == "diyidixue.png":
                        strPlayType = "firstblood"
                        """
                        elif strPlayType == "fengmang3.png":
                            strPlayType = "combothree"
                        elif strPlayType == "fe3ngmang3.png":
                            strPlayType = "combofour"
                        elif strPlayType == "wuren5.png":
                            strPlayType = "combofive"
                        elif strPlayType == "hengsao6.png":
                            strPlayType = "combosix"
                        elif strPlayType == "tianxia7.png":
                            strPlayType = "comboseven"
                        """
                    elif strPlayType == "erliangsha.png":
                        strPlayType = "combotwo"
                    elif strPlayType == "sanliansha.png":
                        strPlayType = "combothree"
                    elif strPlayType == "siliansha.png":
                        strPlayType = "combofour"
                    elif strPlayType == "wuliansha.png":
                        strPlayType = "combofive"
                    elif strPlayType == "fengmang3.png":
                        strPlayType = "fengmangbilou"
                    elif strPlayType == "fengmang3.png":
                        strPlayType = "fengmangbilou"
                    elif strPlayType == "hengsao6.png":
                        strPlayType = "hengsaoqianjun"
                    elif strPlayType == "tianxia7.png":
                        strPlayType = "tianxiawushuang"
                    elif strPlayType == "wujian4.png":
                        strPlayType = "wujianbucui"
                    elif strPlayType == "wuren5.png":
                        strPlayType = "wurennengdang"
                    else:
                        logging.debug("wzry not support jisha {} frameIndex{}".format(strPlayType,dictJiSha["frameIndex"]))
                        continue

                    if dictJiSha["left"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"

                    elif dictJiSha['left'] in objMatchData.arrayRedTeam:
                        strTeam  = "red"

                    else:
                        logging.debug("jisha team hero not valid [{}]".format(dictJiSha))
                        strTeam = "none"

                    post.normalPost(objResult, strTeam, strPlayType,
                                    dictJiSha["frameIndex"])

                    #print(dictJiSha)
                #wzry 的结果
                elif objResult.result == "tuita":
                    dictTuiTa = pickle.loads(objResult.value)

                    #判断连续帧的影响
                    if objMatchData.intLastDestroyTowerTimestamp != 0:
                        if  timeHelp.getNow() - objMatchData.intLastDestroyTowerTimestamp <= 100 or \
                            abs(dictTuiTa["frameIndex"] - objMatchData.intLastDestroyTowerFrameIndex) <= 30:
                            logging.debug("连续帧的推塔信息,pass [{}]".format(dictTuiTa["frameIndex"]))
                            continue

                    if dictTuiTa["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                        objMatchData.intBlueDestroyTowerNum += 1

                    elif dictTuiTa['hero'] in objMatchData.arrayRedTeam:
                        strTeam  = "red"
                        objMatchData.intRedDestroyTowerNum += 1

                    else:
                        logging.debug("tuita team hero not valid [{}]".format(dictTuiTa))
                        strTeam = "none"

                    objMatchData.strLastDestroyHero = dictTuiTa["hero"]
                    objMatchData.intLastDestroyTowerFrameIndex = dictTuiTa["frameIndex"]
                    objMatchData.intLastDestroyTowerTimestamp = timeHelp.getNow()

                    if (objMatchData.intBlueDestroyTowerNum + objMatchData.intRedDestroyTowerNum) == 1:
                        #俩队推塔和 = 1
                        post.normalPost(objResult, strTeam,
                                    "firsttower",
                                        dictTuiTa["frameIndex"])

                elif objResult.result == "dragon":
                    dictDragon = pickle.loads(objResult.value)
                    if dictDragon["dragonType"] == "baojun":
                        if objMatchData.intLastKillBaoJunTimestamp != 0:
                            if (timeHelp.getNow() - objMatchData.intLastKillBaoJunTimestamp) < 10 or \
                                abs(dictDragon["frameIndex"] - objMatchData.intLastKillBaoJunFrameIndex) <= 30:
                                    #objMatchData.strLastKillBaoJunHero == dictDragon["hero"]:
                                    logging.debug("连续帧的杀暴君信息,pass [{}]".format(dictDragon["frameIndex"]))
                                    continue

                    elif dictDragon["dragonType"] == "heianbaojun":
                        if objMatchData.intLastKillBaoJunTimestamp != 0:
                            if (timeHelp.getNow() - objMatchData.intLastKillHeiAnBaoJunTimestamp) < 10 or \
                                abs(dictDragon["frameIndex"] - objMatchData.intLastKillHeiAnBaoJunFrameIndex) <= 30:
                                    #objMatchData.strLastKillBaoJunHero == dictDragon["hero"]:
                                    logging.debug("连续帧的杀黑暗暴君信息,pass [{}]".format(dictDragon["frameIndex"]))
                                    continue

                    else:
                        if objMatchData.intLastKillZhuZaiTimestamp != 0:
                            if (timeHelp.getNow() - objMatchData.intLastKillZhuZaiTimestamp) < 10 or \
                                abs(dictDragon["frameIndex"] - objMatchData.intLastKillZhuZaiFrameIndex) <= 30:
                                    #objMatchData.strLastKillZhuZaiHero == dictDragon["hero"]:
                                    logging.debug("连续帧的杀主宰信息,pass [{}]".format(dictDragon["frameIndex"]))
                                    continue


                    if dictDragon["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                        if dictDragon["dragonType"] == "baojun":
                            objMatchData.intBlueKillBaoJunNum += 1
                        if dictDragon["dragonType"] == "heianbaojun":
                            objMatchData.intBlueKillHeiAnBaoJunNum += 1
                        else:
                            objMatchData.intBlueKillZhuZaiNum += 1


                    elif dictDragon['hero'] in objMatchData.arrayRedTeam:
                        strTeam  = "red"
                        if dictDragon["dragonType"] == "baojun":
                            objMatchData.intRedKillBaoJunNum += 1
                        if dictDragon["dragonType"] == "heianbaojun":
                            objMatchData.intRedKillHeiAnBaoJunNum += 1
                        else:
                            objMatchData.intRedKillZhuZaiNum += 1
                    else:
                        logging.debug("dragon team hero not valid [{}]".format(dictDragon))
                        strTeam = "none"

                    if dictDragon["dragonType"] == "baojun":
                        objMatchData.intLastKillBaoJunTimestamp = timeHelp.getNow()
                        objMatchData.strLastKillBaoJunHero = dictDragon["hero"]
                        objMatchData.intLastKillBaoJunFrameIndex = dictDragon["frameIndex"]

                        if (objMatchData.intBlueKillBaoJunNum + objMatchData.intRedKillBaoJunNum) == 1:
                            # 俩队杀暴君和 = 2
                            post.normalPost(objResult, strTeam,
                                            "firstbaojun",
                                            dictDragon["frameIndex"])
                        elif (objMatchData.intBlueKillBaoJunNum + objMatchData.intRedKillBaoJunNum) == 2:
                            # 俩队杀暴君和 = 2
                            post.normalPost(objResult, strTeam,
                                            "twobaojun",
                                            dictDragon["frameIndex"])


                    elif dictDragon["dragonType"] == "heianbaojun":
                        objMatchData.intLastKillHeiAnBaoJunTimestamp = timeHelp.getNow()
                        objMatchData.strLastKillHeiAnBaoJunHero = dictDragon["hero"]
                        objMatchData.intLastKillHeiAnBaoJunFrameIndex = dictDragon["frameIndex"]

                        if (objMatchData.intBlueKillHeiAnBaoJunNum + objMatchData.intRedKillHeiAnBaoJunNum) == 1:
                            # 俩队杀黑暗暴君和 = 2
                            post.normalPost(objResult, strTeam,
                                            "firstheianbaojun",
                                            dictDragon["frameIndex"])
                        elif (objMatchData.intBlueKillHeiAnBaoJunNum + objMatchData.intRedKillHeiAnBaoJunNum) == 2:
                            # 俩队杀黑暗暴君和 = 2
                            post.normalPost(objResult, strTeam,
                                            "twobaoheianjun",
                                            dictDragon["frameIndex"])

                    else:
                        objMatchData.intLastKillZhuZaiTimestamp = timeHelp.getNow()
                        objMatchData.strLastKillZhuZaiHero = dictDragon["hero"]
                        objMatchData.intLastKillZhuZaiFrameIndex = dictDragon["frameIndex"]

                        if (objMatchData.intBlueKillZhuZaiNum + objMatchData.intRedKillZhuZaiNum) == 1:
                            # 俩队杀主宰和 = 2
                            post.normalPost(objResult, strTeam,
                                            "firstdragon",
                                            dictDragon["frameIndex"])

                        elif (objMatchData.intBlueKillZhuZaiNum + objMatchData.intRedKillZhuZaiNum) == 2:
                            # 俩队杀主宰和 = 2
                            post.normalPost(objResult, strTeam,
                                            "twodragon",
                                            dictDragon["frameIndex"])


                # lol,wzry 的结果
                elif objResult.result == "endGame":
                    intCheckNum = objMatchData.addEndCheckNum()
                    #记录上一次比赛结束最后一帧
                    objMatchData.intLastResultFrameIndex = int(objResult.value)

                    #TODO  設置 重置的地方
                    logging.debug("endGame checkNum[{}] scanIndex[{}] endFrame[{}]".format(intCheckNum,objResult.value,objMatchData.getEndGameIndex()))

                    objMatchData.intCheckWinLastTime = timeHelp.getNow()
                    if intCheckNum > serviceConfig.tempBase  and objMatchData.getCheckWinIndex() == 0:
                        logging.debug("endGame more than {} frame".format(serviceConfig.tempBase))
                        intCheckWinIndex = int(objResult.value)
                        objMatchData.setCheckWinIndex(intCheckWinIndex - serviceConfig.tempBase - serviceConfig.checkWinFrameNum - serviceConfig.queueSizeEndModify)
                        objMatchData.setEndGameIndex(intCheckWinIndex - serviceConfig.tempBase - serviceConfig.queueSizeEndModify)
                        objMatchData.setCheckScoreIndex(intCheckWinIndex - serviceConfig.tempBase - serviceConfig.checkScoreFrameNum - serviceConfig.queueSizeEndModify)
                        objMatchData.setGameState("checkScore")
                        #return

                # lol,wzry 的结果
                elif objResult.result == "winTeam":
                    dictResult = pickle.loads(objResult.value)
                    logging.debug("check win[{}]".format(dictResult))

                    if dictResult['win'] == "blue":
                        objMatchData.addBlueWin()
                    else:
                        objMatchData.addRedWin()

                    #strTeam = ""
                    #這一陣需要計算進去
                    if objMatchData.getEndGameIndex() - 1 <= dictResult['frameIndex']:
                        iBlueNum,iRedNum = objMatchData.getWinNum()
                        if iRedNum <= 0 and iBlueNum <= 0:
                            # 如果俩个都是0,就是有问题的
                            pass
                        else:
                            logging.debug("blueNum[{}] redNum[{}]".format(iBlueNum, iRedNum))
                            if iBlueNum > iRedNum:
                                strTeam = "blue"
                            elif iBlueNum < iRedNum:
                                strTeam = "red"
                            else:
                                logging.debug("winTeam not valid")
                                strTeam = "none"

                            if objMatchData.strMatchType == "lol":
                                post.normalPostWithParam(objResult, strTeam, "roundEnd", dictResult["frameIndex"],
                                                         json.dumps(
                                                             {"iATeamKills": int(objMatchData.intBlueKill),
                                                              "iBTeamKills": int(objMatchData.intRedKill),
                                                              "iATeamTowers": int(objMatchData.intBlueDestroyTower),
                                                              "iBTeamTowers": int(objMatchData.intRedDestroyTower),
                                                              "iATeamBarons": int(objMatchData.intBlueKillBigDragonNum),
                                                              "iBTeamBarons": int(objMatchData.intRedKillBigDragonNum),
                                                              "iATeamDragons": int(objMatchData.intBlueKillSmallDragonNum),
                                                              "iBTeamDragons": int(objMatchData.intRedKillSmallDragonNum),
                                                              #先默认,TODO
                                                              "iATeamScore": 0, "iBTeamScore": 0}))
                            else:
                                post.normalPostWithParam(objResult,strTeam,"roundEnd", dictResult["frameIndex"], json.dumps(
                                        {"iATeamKills": int(objMatchData.intBlueKill),
                                         "iBTeamKills": int(objMatchData.intRedKill),
                                         "iATeamTowers": int(objMatchData.intBlueDestroyTower),
                                         "iBTeamTowers": int(objMatchData.intRedDestroyTower),
                                         "iATeamBarons": int(objMatchData.intBlueKillZhuZaiNum),
                                         "iBTeamBarons": int(objMatchData.intRedKillZhuZaiNum),
                                         "iATeamDragons": int(objMatchData.intBlueKillBaoJunNum),
                                         "iBTeamDragons": int(objMatchData.intRedKillBaoJunNum),
                                         #先默认,TODO
                                         "iATeamScore": 0, "iBTeamScore": 0}))

                # lol,wzry 的结果
                elif objResult.result == "scores":
                    dictResult = pickle.loads(objResult.value)
                    logging.debug("check score[{}]".format(dictResult))
                    logging.debug("endGameIndex [{}]".format(objMatchData.getEndGameIndex()))

                    if objMatchData.getEndGameIndex() - serviceConfig.checkEndScoreFrameNum > dictResult['frameIndex']:

                        if objResult.strMatchType == "lol":
                            if len(dictResult) != 5:
                                logging.debug("check score len not valid {}".format(dictResult))
                                continue
                        else:
                            if len(dictResult) != 3:
                                logging.debug("check score len not valid {}".format(dictResult))
                                continue

                        #比分检测完毕,检测谁输谁赢
                        if "leftKill" in dictResult:
                            objMatchData.intBlueKill = "0" if len(dictResult["leftKill"])<= 0 else dictResult["leftKill"]
                        if "rightKill" in dictResult:
                            objMatchData.intRedKill = "0" if len(dictResult["rightKill"])<= 0 else dictResult["rightKill"]
                        if "leftTower" in dictResult:
                            objMatchData.intBlueDestroyTower = "0" if len(dictResult["leftTower"])<= 0 else dictResult["leftTower"]
                        if "rightTower" in dictResult:
                            objMatchData.intRedDestroyTower = "0" if len(dictResult["rightTower"])<= 0 else dictResult["rightTower"]

                        objMatchData.setGameState("checkWin")

                    else:
                        #如果帧数已经超过了，比分不检测也要结束到这局比赛
                        objMatchData.setGameState("checkWin")

                #lol 的结果
                elif objResult.result == "lol_dragonAtt":
                    dictResult = pickle.loads(objResult.value)
                    if dictResult['att'] == "tulong":
                        postType = 1
                    elif dictResult['att'] == "shuilong":
                        postType = 2
                    elif dictResult['att'] == "yunlong":
                        postType = 3
                    elif dictResult['att'] == "huolong":
                        postType = 4
                    else:
                        logging.debug("dragon att type not valid")
                        continue

                    if len(objMatchData.strFirstDragonAtt) > 0:
                        continue

                    objMatchData.strFirstDragonAtt = dictResult['att']
                    post.normalPostWithParamWithoutTeam(objResult,"firstdragontype",
                                                        postType,dictResult["frameIndex"])

                elif objResult.result == "lol_tenKill":
                    dictResult = pickle.loads(objResult.value)
                    print("10杀 [{}]".format(dictResult))

                    post.normalPost(objResult,dictResult["team"],"tenkill",
                                    dictResult["frameIndex"])

                elif objResult.result == "lol_firstTower":
                    dictResult = pickle.loads(objResult.value)

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayRedTeam:
                        strTeam = "red"
                    else:
                        logging.debug("first tower hero[{}] not valid".format(dictResult["hero"]))
                        strTeam = "none"

                    if objMatchData.intFirstTowerFrame != 0:
                        if abs(objMatchData.intFirstTowerFrame - dictResult["frameIndex"]) < 300:
                            print("连续帧 一塔 信息 {}".format(objMatchData.intFirstTowerFrameNum))
                            if objMatchData.intFirstTowerFrameNum == 5:
                                post.normalPost(objResult, strTeam, "firsttower",
                                                dictResult["frameIndex"])

                    print("一塔 xxxx [{}]".format(dictResult["frameIndex"]))
                    objMatchData.intFirstTowerFrame = dictResult["frameIndex"]
                    objMatchData.intFirstTowerFrameNum += 1


                elif objResult.result == "lol_xiaGuXianFeng":
                    dictResult = pickle.loads(objResult.value)
                    print("击杀xiaguxianfeng {}".format(dictResult))

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayRedTeam:
                        strTeam = "red"
                    else:
                        logging.debug("small dragon hero[{}] not valid".format(dictResult["hero"]))
                        strTeam = "none"

                    if objMatchData.intXianGuXianFengFrame != 0:
                        if abs(objMatchData.intXianGuXianFengFrame - dictResult["frameIndex"]) < 300:
                            print("连续帧的 xiaguxianfeng 信息 {}".format(objMatchData.intXianGuXianFengFrameNum))
                            if objMatchData.intXianGuXianFengFrameNum == 5:
                                post.normalPost(objResult, strTeam, "firstxianfeng",
                                                dictResult["frameIndex"])

                    print("xiaguxianfeng xxxx [{}]".format(dictResult["frameIndex"]))
                    objMatchData.intXianGuXianFengFrame = dictResult["frameIndex"]
                    objMatchData.intXianGuXianFengFrameNum += 1




                elif objResult.result == "lol_smallDragon":
                    dictResult = pickle.loads(objResult.value)
                    print("击杀小龙 {}".format(dictResult))

                    if abs(objMatchData.intSmallDragonFrame - dictResult["frameIndex"]) <= 300 or\
                        timeHelp.getNow() - objMatchData.intLastKillSmallDragonTimestamp <= 60:
                        #objMatchData.dictResult["hero"] ==
                        logging.debug("连续帧的击杀小龙 [{}]".format(dictResult["frameIndex"] ))
                        continue

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                        objMatchData.intBlueKillSmallDragonNum += 1
                    elif dictResult["hero"] in objMatchData.arrayRedTeam:
                        strTeam = "red"
                        objMatchData.intRedKillSmallDragonNum += 1
                    else:
                        logging.debug("small dragon hero[{}] not valid".format(dictResult["hero"]))
                        objMatchData.intBlueKillSmallDragonNum += 1
                        strTeam = "none"
                        #continue

                    print("击杀小龙 xxxx [{}]".format(dictResult["frameIndex"]))
                    objMatchData.intSmallDragonFrame = dictResult["frameIndex"]
                    objMatchData.strKillSmallDragonHero = dictResult["hero"]
                    objMatchData.intLastKillSmallDragonTimestamp = timeHelp.getNow()

                    if (objMatchData.intBlueKillSmallDragonNum+objMatchData.intRedKillSmallDragonNum) == 2:
                        post.normalPost(objResult,strTeam,"twodragon",
                                        dictResult["frameIndex"])

                elif objResult.result == "lol_bigDragon":
                    dictResult = pickle.loads(objResult.value)
                    print("击杀大龙 {}".format(dictResult))

                    if abs(objMatchData.intBigDragonFrame - dictResult["frameIndex"]) <= 300 or\
                        timeHelp.getNow() - objMatchData.intLastKillBigDragonTimestamp <= 60:
                        #objMatchData.dictResult["hero"] ==
                        logging.debug("连续帧的击杀大龙 [{}]".format(dictResult["frameIndex"] ))
                        continue

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                        objMatchData.intBlueKillBigDragonNum += 1
                    elif dictResult["hero"] in objMatchData.arrayRedTeam:
                        strTeam = "red"
                        objMatchData.intRedKillBigDragonNum += 1
                    else:
                        logging.debug("big dragon hero[{}] not valid".format(dictResult["hero"]))
                        strTeam = "none"
                        #默认挑一个+1
                        objMatchData.intBlueKillBigDragonNum += 1

                    print("击杀大龙 xxxx [{}]".format(dictResult["frameIndex"]))
                    objMatchData.intBigDragonFrame = dictResult["frameIndex"]
                    objMatchData.strKillBigDragonHero = dictResult["hero"]
                    objMatchData.intLastKillBigDragonTimestamp = timeHelp.getNow()

                    if (objMatchData.intBlueKillBigDragonNum + objMatchData.intRedKillBigDragonNum) == 1:
                        post.normalPost(objResult,strTeam,"firstbaron",
                                        dictResult["frameIndex"])


                elif objResult.result == "lol_firstBlood":
                    dictResult = pickle.loads(objResult.value)


                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayRedTeam:
                        strTeam = "red"
                    else:
                        logging.debug("five blood hero[{}] not valid".format(dictResult["hero"]))
                        strTeam = "none"


                    if objMatchData.intFirstBloodFrame != 0:
                        if abs(objMatchData.intFirstBloodFrame - dictResult["frameIndex"]) < 300:
                            print("连续帧的 一血 信息 {}".format(objMatchData.intFirstBloodFrameNum))
                            if objMatchData.intFirstBloodFrameNum == 5:
                                post.normalPost(objResult, strTeam, "firstblood",
                                                dictResult["frameIndex"])

                    print("一血 xxxx [{}]".format(dictResult["frameIndex"]))
                    objMatchData.intFirstBloodFrame = dictResult["frameIndex"]
                    objMatchData.intFirstBloodFrameNum += 1

                elif objResult.result == "lol_fiveKill":
                    dictResult = pickle.loads(objResult.value)
                    print("5杀 {}".format(dictResult))

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayRedTeam:
                        strTeam = "red"
                    else:
                        logging.debug("five kill hero[{}] not valid".format(dictResult["hero"]))
                        strTeam = "none"

                    if objMatchData.intFiveKillFrame != 0:
                        if abs(objMatchData.intFiveKillFrame - dictResult["frameIndex"]) < 300:
                            print("连续帧的 五杀 信息 {}".format(objMatchData.intFiveKillFrameNum))
                            if objMatchData.intFiveKillFrameNum == 5:
                                post.normalPost(objResult, strTeam,
                                                "fivekill",
                                                dictResult["frameIndex"])

                    print("五杀 xxxx [{}]".format(dictResult["frameIndex"]))
                    objMatchData.intFiveKillFrame = dictResult["frameIndex"]
                    objMatchData.intFiveKillFrameNum += 1

                elif objResult.result == "lol_fourKill":
                    dictResult = pickle.loads(objResult.value)
                    print("4杀 {}".format(dictResult))

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayRedTeam:
                        strTeam = "red"
                    else:
                        logging.debug("four kill hero[{}] not valid".format(dictResult["hero"]))
                        strTeam = "none"

                    if objMatchData.intFourKillFrame != 0:
                        if abs(objMatchData.intFourKillFrame - dictResult["frameIndex"]) < 300:
                            print("连续帧的 四杀 信息 {}".format(objMatchData.intFourKillFrameNum))
                            if objMatchData.intFourKillFrameNum == 5:
                                post.normalPost(objResult, strTeam,
                                                "fourkill",
                                                dictResult["frameIndex"])

                    print("4杀 xxxx [{}]".format(dictResult["frameIndex"]))
                    objMatchData.intFourKillFrame = dictResult["frameIndex"]
                    objMatchData.intFourKillFrameNum += 1


                elif objResult.result == "lol_threeKill":
                    dictResult = pickle.loads(objResult.value)
                    print("3杀 {}".format(dictResult))

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayRedTeam:
                        strTeam = "red"
                    else:
                        logging.debug("three kill hero[{}] not valid".format(dictResult["hero"]))
                        strTeam = "none"

                    if objMatchData.intThreeKillFrame != 0:
                        if abs(objMatchData.intThreeKillFrame - dictResult["frameIndex"]) < 300:
                            print("连续帧的 三杀 信息 {}".format(objMatchData.intThreeKillFrameNum))
                            if objMatchData.intThreeKillFrameNum == 5:
                                post.normalPost(objResult, strTeam,
                                                "threekill",
                                                dictResult["frameIndex"])

                    print("3杀 xxxx [{}]".format(dictResult["frameIndex"]))
                    objMatchData.intThreeKillFrame = dictResult["frameIndex"]
                    objMatchData.intThreeKillFrameNum += 1



                elif objResult.result == "lol_godLike":
                    dictResult = pickle.loads(objResult.value)
                    print("超神 {}".format(dictResult))

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayRedTeam:
                        strTeam = "red"
                    else:
                        logging.debug("god like hero[{}] not valid".format(dictResult["hero"]))
                        strTeam = "none"

                    if objMatchData.intGoldLikeFrame != 0:
                        if abs(objMatchData.intGoldLikeFrame - dictResult["frameIndex"]) < 300:
                            print("连续帧的 超神 信息")
                            if objMatchData.intGoldLikeFrameNum == 5:
                                post.normalPost(objResult, strTeam,
                                                "comboeight",
                                                dictResult["frameIndex"])

                    print("超神 xxxx {}".format(dictResult["frameIndex"]))
                    objMatchData.intGoldLikeFrame = dictResult["frameIndex"]
                    objMatchData.intGoldLikeFrameNum += 1


                elif objResult.result == "replayGame":
                    #dictResult = pickle.loads(objResult.value)
                    #是录像,重置那个最后的check计数
                    objMatchData.resetEndCheckNum()
                    objMatchData.intCheckWinLastTime = 0
                else:
                    #print("reset end and time")
                    objMatchData.resetEndCheckNum()
                    objMatchData.intCheckWinLastTime = 0


                    objMatchData.intFirstTowerFrameNum = 0
                    objMatchData.intXianGuXianFengFrameNum=0
                    objMatchData.intFiveKillFrameNum = 0
                    objMatchData.intFourKillFrameNum = 0
                    objMatchData.intThreeKillFrameNum = 0
                    objMatchData.intGoldLikeFrameNum = 0
                    objMatchData.intFirstBloodFrameNum = 0
            else:
                time.sleep(1)
