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
                            logging.debug("blue team {}".format(var))
                        for var in objMatchData.arrayRedTeam:
                            logging.debug("red team {}".format(var))

                    objMatchData.setGameState("fighting")

                # wzry 的结果
                elif objResult.result == "jisha":
                    dictJiSha = pickle.loads(objResult.value)
                    strPlayType = dictJiSha["des"]

                    if strPlayType == "diyidixue.png":
                        strPlayType = "firstblood"
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
                    else:
                        logging.debug("wzry not support jisha {} frameIndex{}".format(strPlayType,dictJiSha["frameIndex"]))
                        continue

                    strTeam = ""
                    if dictJiSha["left"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"

                    elif dictJiSha['left'] in objMatchData.arrayRedTeam:
                        strTeam  = "red"

                    else:
                        logging.debug("jisha team hero not valid [{}]".format(dictJiSha))
                        continue

                    post.normalPost(objResult, strTeam, strPlayType,
                                    dictJiSha["frameIndex"])

                    #print(dictJiSha)
                #wzry 的结果
                elif objResult.result == "tuita":
                    dictTuiTa = pickle.loads(objResult.value)

                    #判断连续帧的影响
                    if dictTuiTa["hero"] == objMatchData.strLastDestroyHero and\
                        timeHelp.getNow() - objMatchData.intLastDestroyTowerTimestamp <= 10 and \
                        abs(dictTuiTa["frameIndex"] - objMatchData.intLastDestroyTowerFrameIndex) <= 30:
                        logging.debug("连续帧的推塔信息,pass [{}]".format(dictTuiTa["frameIndex"]))
                        continue

                    strTeam = ""
                    if dictTuiTa["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                        objMatchData.intBlueDestroyTowerNum += 1


                    elif dictTuiTa['hero'] in objMatchData.arrayRedTeam:
                        strTeam  = "red"
                        objMatchData.intRedDestroyTowerNum += 1

                    else:
                        logging.debug("tuita team hero not valid [{}]".format(dictTuiTa))
                        continue

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
                        if (timeHelp.getNow() - objMatchData.intLastKillBaoJunTimestamp) < 10 and \
                            abs(dictDragon["frameIndex"] - objMatchData.intLastKillBaoJunFrameIndex) <= 30 and \
                                objMatchData.strLastKillBaoJunHero == dictDragon["hero"]:
                                logging.debug("连续帧的杀龙信息,pass [{}]".format(dictDragon["frameIndex"]))
                                continue

                    else:
                        if (timeHelp.getNow() - objMatchData.intLastKillZhuZaiTimestamp) < 10 and \
                            abs(dictDragon["frameIndex"] - objMatchData.intLastKillZhuZaiFrameIndex) <= 30 and \
                                objMatchData.strLastKillZhuZaiHero == dictDragon["hero"]:
                                logging.debug("连续帧的杀龙信息,pass [{}]".format(dictDragon["frameIndex"]))
                                continue


                    strTeam = ""
                    if dictDragon["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                        if dictDragon["dragonType"] == "baojun":
                            objMatchData.intBlueKillBaoJunNum += 1
                        else:
                            objMatchData.intBlueKillZhuZaiNum += 1
                    elif dictDragon['hero'] in objMatchData.arrayRedTeam:
                        strTeam  = "red"
                        if dictDragon["dragonType"] == "baojun":
                            objMatchData.intRedKillBaoJunNum += 1
                        else:
                            objMatchData.intRedKillZhuZaiNum += 1
                    else:
                        logging.debug("dragon team hero not valid [{}]".format(dictDragon))
                        continue

                    if dictDragon["dragonType"] == "baojun":
                        objMatchData.intLastKillBaoJunTimestamp = timeHelp.getNow()
                        objMatchData.strLastKillBaoJunHero = dictDragon["hero"]
                        objMatchData.intLastKillBaoJunFrameIndex = dictDragon["frameIndex"]
                    else:
                        objMatchData.intLastKillZhuZaiTimestamp = timeHelp.getNow()
                        objMatchData.strLastKillZhuZaiHero = dictDragon["hero"]
                        objMatchData.intLastKillZhuZaiFrameIndex = dictDragon["frameIndex"]

                    if (objMatchData.intBlueKillBaoJunNum + objMatchData.intRedKillBaoJunNum) == 1:
                        #俩队杀暴君和 = 2
                        post.normalPost(objResult, strTeam,
                                    "firstbaojun",
                                        dictDragon["frameIndex"])

                    elif (objMatchData.intBlueKillZhuZaiNum + objMatchData.intRedKillZhuZaiNum) == 1:
                        #俩队杀主宰和 = 2
                        post.normalPost(objResult, strTeam,
                                    "firstdragon",
                                        dictDragon["frameIndex"])

                    elif (objMatchData.intBlueKillBaoJunNum + objMatchData.intRedKillBaoJunNum) == 2:
                        #俩队杀暴君和 = 2
                        post.normalPost(objResult, strTeam,
                                    "twobaojun",
                                        dictDragon["frameIndex"])

                    elif (objMatchData.intBlueKillZhuZaiNum + objMatchData.intRedKillZhuZaiNum) == 2:
                        #俩队杀主宰和 = 2
                        post.normalPost(objResult, strTeam,
                                    "twodragon",
                                        dictDragon["frameIndex"])

                # lol,wzry 的结果
                elif objResult.result == "endGame":
                    intCheckNum = objMatchData.addEndCheckNum()
                    #TODO  設置 重置的地方
                    logging.debug("endGame checkNum[{}] scanIndex[{}]".format(intCheckNum,objResult.value))

                    if intCheckNum > serviceConfig.tempBase  and objMatchData.getCheckWinIndex() == 0:
                        logging.debug("endGame more than 30s")
                        intCheckWinIndex = int(objResult.value)
                        objMatchData.setCheckWinIndex(intCheckWinIndex - serviceConfig.tempBase - serviceConfig.checkWinFrameNum)
                        objMatchData.setEndGameIndex(intCheckWinIndex - serviceConfig.tempBase)
                        objMatchData.setCheckScoreIndex(intCheckWinIndex - serviceConfig.tempBase - serviceConfig.checkScoreFrameNum)
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
                                continue

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
                    if objMatchData.getEndGameIndex() - serviceConfig.checkEndScoreFrameNum <= dictResult['frameIndex']:
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

                #lol 的结果
                elif objResult.result == "lol_dragonAtt":
                    dictResult = pickle.loads(objResult.value)
                    if dictResult['att'] == "tulong":
                        postType = 1
                    elif dictResult['att'] == "shuilong":
                        postType = 2
                    elif dictResult['att'] == "fenglong":
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

                    post.normalPost(objResult,dictResult["team"],"tenkill",
                                    dictResult["frameIndex"])

                elif objResult.result == "lol_firstTower":
                    dictResult = pickle.loads(objResult.value)

                    post.normalPost(objResult,dictResult["team"],"firsttower",
                                    dictResult["frameIndex"])


                elif objResult.result == "lol_xiaGuXianFeng":
                    dictResult = pickle.loads(objResult.value)

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "red"
                    else:
                        logging.debug("small dragon hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    post.normalPost(objResult,strTeam,"firstxianfeng",
                                    dictResult["frameIndex"])

                elif objResult.result == "lol_smallDragon":
                    dictResult = pickle.loads(objResult.value)

                    if abs(objMatchData.intSmallDragonFrame - dictResult["frameIndex"] <= 30) and\
                        timeHelp.getNow() - objMatchData.intLastKillSmallDragonTimestamp <= 2:
                        #objMatchData.dictResult["hero"] ==
                        logging.debug("连续帧的击杀小龙 [{}]".format(dictResult["frameIndex"] ))
                        continue

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                        objMatchData.intBlueKillSmallDragonNum += 1
                    elif dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "red"
                        objMatchData.intRedKillSmallDragonNum += 1
                    else:
                        logging.debug("small dragon hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    objMatchData.strKillSmallDragonHero = dictResult["hero"]
                    objMatchData.intLastSmallDragonTimestamp = timeHelp.getNow()

                    if (objMatchData.intBlueKillSmallDragonNum+objMatchData.intRedKillSmallDragonNum) == 2:
                        post.normalPost(objResult,strTeam,"twodragon",
                                        dictResult["frameIndex"])



                elif objResult.result == "lol_bigDragon":
                    dictResult = pickle.loads(objResult.value)

                    if abs(objMatchData.intBigDragonFrame - dictResult["frameIndex"] <= 30) and\
                        timeHelp.getNow() - objMatchData.intLastKillBigDragonTimestamp <= 2:
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
                        continue


                    objMatchData.strKillBigDragonHero = dictResult["hero"]
                    objMatchData.intLastKillBigDragonTimestamp = timeHelp.getNow()

                    if (objMatchData.intBlueKillBigDragonNum + objMatchData.intRedKillBigDragonNum) == 1:
                        post.normalPost(objResult,strTeam,"firstbaron",
                                        dictResult["frameIndex"])


                elif objResult.result == "lol_firstBlood":
                    dictResult = pickle.loads(objResult.value)

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "red"
                    else:
                        logging.debug("five blood hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    post.normalPost(objResult,strTeam,"firstblood",
                                    dictResult["frameIndex"])

                elif objResult.result == "lol_fiveKill":
                    dictResult = pickle.loads(objResult.value)

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "red"
                    else:
                        logging.debug("five kill hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    post.normalPost(objResult, strTeam,
                                    "fivekill",
                                    dictResult["frameIndex"])

                elif objResult.result == "lol_godLike":
                    dictResult = pickle.loads(objResult.value)

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "red"
                    else:
                        logging.debug("god like hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    post.normalPost(objResult,strTeam,
                                    "comboeight",
                                    dictResult["frameIndex"])
                elif objResult.result == "replayGame":
                    #dictResult = pickle.loads(objResult.value)
                    #是录像,重置那个最后的check计数
                    objMatchData.resetEndCheckNum()

                else:
                    pass
            else:
                time.sleep(1)
