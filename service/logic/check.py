from service.singleton import singletonInstance
from service import serviceConfig
from service.logic import post
from lib.timehelp import timeHelp
import pickle
import json
import time

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
                    print("error match data is None")
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
                    print(listTotalTeam)
                    #TODO 可以查看到返回值和当前队伍的队员是否一致,需要计算队员
                    if objResult.strMatchType == "lol":
                        for var in listTotalTeam[0:5]:
                            if var[0] > 0.15:
                                print("{} {} may be wrong".format(var[0],var[2]))

                            objMatchData.arrayBlueTeam.append(var[2])
                        for var in listTotalTeam[5:10]:
                            if var[0] > 0.15:
                                print("{} {} may be wrong".format(var[0], var[2]))

                            objMatchData.arrayRedTeam.append(var[2])
                    else:
                        objMatchData.arrayBlueTeam = listTotalTeam[0:5]
                        objMatchData.arrayRedTeam = listTotalTeam[5:10]

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
                        print("wzry not support jisha {} frameIndex{}".format(strPlayType,dictJiSha["frameIndex"]))
                        continue

                    strTeam = ""
                    if dictJiSha["left"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"

                    elif dictJiSha['left'] in objMatchData.arrayRedTeam:
                        strTeam  = "red"

                    else:
                        print("jisha team hero not valid [{}]".format(dictJiSha))
                        continue

                    post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound, strTeam, strPlayType,
                                    dictJiSha["frameIndex"])

                    #print(dictJiSha)
                #wzry 的结果
                elif objResult.result == "tuita":
                    dictTuiTa = pickle.loads(objResult.value)

                    #判断连续帧的影响
                    if dictTuiTa["hero"] == objMatchData.strLastDestroyHero and\
                        timeHelp.getNow() - objMatchData.intLastDestroyTowerTimestamp <= 10 and \
                        abs(dictTuiTa["frameIndex"] - objMatchData.intLastDestroyTowerFrameIndex) <= 30:
                        print("连续帧的推塔信息,pass [{}]".format(dictTuiTa["frameIndex"]))
                        continue

                    strTeam = ""
                    if dictTuiTa["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                        objMatchData.intBlueDestroyTowerNum += 1


                    elif dictTuiTa['hero'] in objMatchData.arrayRedTeam:
                        strTeam  = "red"
                        objMatchData.intRedDestroyTowerNum += 1

                    else:
                        print("tuita team hero not valid [{}]".format(dictTuiTa))
                        continue

                    objMatchData.strLastDestroyHero = dictTuiTa["hero"]
                    objMatchData.intLastDestroyTowerFrameIndex = dictTuiTa["frameIndex"]
                    objMatchData.intLastDestroyTowerTimestamp = timeHelp.getNow()

                    if (objMatchData.intBlueDestroyTowerNum + objMatchData.intRedDestroyTowerNum) == 1:
                        #俩队推塔和 = 1
                        post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound, strTeam,
                                    "firsttower",
                                        dictTuiTa["frameIndex"])

                elif objResult.result == "dragon":
                    dictDragon = pickle.loads(objResult.value)
                    if dictDragon["dragonType"] == "baojun":
                        if (timeHelp.getNow() - objMatchData.intLastKillBaoJunTimestamp) < 10 and \
                            abs(dictDragon["frameIndex"] - objMatchData.intLastKillBaoJunFrameIndex) <= 30 and \
                                objMatchData.strLastKillBaoJunHero == dictDragon["hero"]:
                                print("连续帧的杀龙信息,pass [{}]".format(dictDragon["frameIndex"]))
                                continue

                    else:
                        if (timeHelp.getNow() - objMatchData.intLastKillZhuZaiTimestamp) < 10 and \
                            abs(dictDragon["frameIndex"] - objMatchData.intLastKillZhuZaiFrameIndex) <= 30 and \
                                objMatchData.strLastKillZhuZaiHero == dictDragon["hero"]:
                                print("连续帧的杀龙信息,pass [{}]".format(dictDragon["frameIndex"]))
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
                        print("dragon team hero not valid [{}]".format(dictDragon))
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
                        post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound, strTeam,
                                    "firstbaojun",
                                        dictDragon["frameIndex"])

                    elif (objMatchData.intBlueKillZhuZaiNum + objMatchData.intRedKillZhuZaiNum) == 1:
                        #俩队杀主宰和 = 2
                        post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound, strTeam,
                                    "firstdragon",
                                        dictDragon["frameIndex"])

                    elif (objMatchData.intBlueKillBaoJunNum + objMatchData.intRedKillBaoJunNum) == 2:
                        #俩队杀暴君和 = 2
                        post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound, strTeam,
                                    "twobaojun",
                                        dictDragon["frameIndex"])

                    elif (objMatchData.intBlueKillZhuZaiNum + objMatchData.intRedKillZhuZaiNum) == 2:
                        #俩队杀主宰和 = 2
                        post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound, strTeam,
                                    "twodragon",
                                        dictDragon["frameIndex"])

                # lol,wzry 的结果
                elif objResult.result == "endGame":
                    intCheckNum = objMatchData.addEndCheckNum()
                    print("endGame checkNum[{}] scanIndex[{}]".format(intCheckNum,objResult.value))

                    if intCheckNum > serviceConfig.tempBase  and objMatchData.getCheckWinIndex() == 0:
                        print("endGame more than 30s")
                        intCheckWinIndex = int(objResult.value)
                        objMatchData.setCheckWinIndex(intCheckWinIndex - serviceConfig.tempBase - serviceConfig.checkWinFrameNum)
                        objMatchData.setEndGameIndex(intCheckWinIndex - serviceConfig.tempBase)
                        objMatchData.setCheckScoreIndex(intCheckWinIndex - serviceConfig.tempBase - serviceConfig.checkScoreFrameNum)
                        objMatchData.setGameState("checkScore")
                        #return

                # lol,wzry 的结果
                elif objResult.result == "winTeam":
                    dictResult = pickle.loads(objResult.value)
                    print("check win[{}]".format(dictResult))

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
                            print("blueNum[{}] redNum[{}]".format(iBlueNum, iRedNum))
                            if iBlueNum > iRedNum:
                                strTeam = "blue"
                            elif iBlueNum < iRedNum:
                                strTeam = "red"
                            else:
                                print("winTeam not valid")
                                continue

                            post.normalPostWithParam(objResult.strMatchType, objResult.strMatchId, objResult.iRound,
                                                     strTeam,
                                                     "roundEnd", dictResult["frameIndex"], json.dumps(
                                    {"iATeamKills": int(objMatchData.strKillHeroLeft),
                                     "iBTeamKills": int(objMatchData.strKillHeroRight), "iATeamTowers": 1,
                                     "iBTeamTowers": 1, "iATeamBarons": int(objMatchData.intBlueKillZhuZaiNum),
                                     "iBTeamBarons": int(objMatchData.intRedKillZhuZaiNum),
                                     "iATeamDragons": int(objMatchData.intBlueKillBaoJunNum),
                                     "iBTeamDragons": int(objMatchData.intRedKillBaoJunNum),
                                     "iATeamScore": 0, "iBTeamScore": 0}))

                # lol,wzry 的结果
                elif objResult.result == "scores":
                    dictResult = pickle.loads(objResult.value)
                    print("check score[{}]".format(dictResult))

                    if objMatchData.getEndGameIndex() - serviceConfig.checkEndScoreFrameNum <= dictResult['frameIndex']:
                        #比分检测完毕,检测谁输谁赢
                        if "leftKill" in dictResult:
                            objMatchData.strKillHeroLeft = "0" if len(dictResult["leftKill"])<= 0 else dictResult["leftKill"]
                        if "rightKill" in dictResult:
                            objMatchData.strKillHeroRight = "0" if len(dictResult["rightKill"])<= 0 else dictResult["rightKill"]

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
                        print("dragon att type not valid")
                        continue

                    if len(objMatchData.strFirstDragonAtt) > 0:
                        continue

                    objMatchData.strFirstDragonAtt = dictResult['att']
                    post.normalPostWithParamWithoutTeam(objResult.strMatchType, objResult.strMatchId, objResult.iRound,"firstdragontype",
                                                        postType,dictResult["frameIndex"])

                elif objResult.result == "lol_tenKill":
                    dictResult = pickle.loads(objResult.value)

                    post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound,dictResult["team"],"tenkill",
                                    dictResult["frameIndex"])

                elif objResult.result == "lol_firstTower":
                    dictResult = pickle.loads(objResult.value)

                    post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound,dictResult["team"],"firsttower",
                                    dictResult["frameIndex"])


                elif objResult.result == "lol_xiaGuXianFeng":
                    dictResult = pickle.loads(objResult.value)

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "red"
                    else:
                        print("small dragon hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound,strTeam,"firstxianfeng",
                                    dictResult["frameIndex"])

                elif objResult.result == "lol_smallDragon":
                    dictResult = pickle.loads(objResult.value)

                    if abs(objMatchData.intSmallDragonFrame - dictResult["frameIndex"] <= 30) and\
                        timeHelp.getNow() - objMatchData.intLastKillSmallDragonTimestamp <= 2:
                        #objMatchData.dictResult["hero"] ==
                        print("连续帧的击杀小龙 [{}]".format(dictResult["frameIndex"] ))
                        continue

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "red"
                    else:
                        print("small dragon hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    objMatchData.intKillSmallDragonNum +=1
                    objMatchData.strKillSmallDragonHero = dictResult["hero"]
                    objMatchData.intLastSmallDragonTimestamp = timeHelp.getNow()

                    if objMatchData.intKillSmallDragonNum == 2:
                        post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound,strTeam,"twodragon",
                                        dictResult["frameIndex"])



                elif objResult.result == "lol_bigDragon":
                    dictResult = pickle.loads(objResult.value)

                    if abs(objMatchData.intBigDragonFrame - dictResult["frameIndex"] <= 30) and\
                        timeHelp.getNow() - objMatchData.intLastKillBigDragonTimestamp <= 2:
                        #objMatchData.dictResult["hero"] ==
                        print("连续帧的击杀大龙 [{}]".format(dictResult["frameIndex"] ))
                        continue

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayRedTeam:
                        strTeam = "red"
                    else:
                        print("big dragon hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    objMatchData.intBigDragonFrame +=1
                    objMatchData.strKillBigDragonHero = dictResult["hero"]
                    objMatchData.intLastKillBigDragonTimestamp = timeHelp.getNow()

                    if objMatchData.intKillBigDragonNum == 1:
                        post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound,strTeam,"firstbaron",
                                        dictResult["frameIndex"])


                elif objResult.result == "lol_firstBlood":
                    dictResult = pickle.loads(objResult.value)

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "red"
                    else:
                        print("five blood hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound,strTeam,"firstblood",
                                    dictResult["frameIndex"])

                elif objResult.result == "lol_fiveKill":
                    dictResult = pickle.loads(objResult.value)

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "red"
                    else:
                        print("five kill hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound, strTeam,
                                    "fivekill",
                                    dictResult["frameIndex"])

                elif objResult.result == "lol_godLike":
                    dictResult = pickle.loads(objResult.value)

                    if dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "blue"
                    elif dictResult["hero"] in objMatchData.arrayBlueTeam:
                        strTeam = "red"
                    else:
                        print("god like hero[{}] not valid".format(dictResult["hero"]))
                        continue

                    post.normalPost(objResult.strMatchType, objResult.strMatchId, objResult.iRound, strTeam,
                                    "comboeight",
                                    dictResult["frameIndex"])

                else:
                    pass
            else:
                time.sleep(1)
