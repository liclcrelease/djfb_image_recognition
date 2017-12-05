import os
import pickle
import sys
import time
import logging
import cv2
import signal
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")
from optparse import OptionParser
from wzry.proc import procVariable
from multiprocessing.managers import BaseManager,ValueProxy,ListProxy,DictProxy
from multiprocessing import Value
from workerSvr.singleton import singletonInstance

#from wzry.logic import checkFighting, checkBegin, checkChoose
#from lol.logic import checkFighting,checkBegin,checkChoose
from wzry.logic.checkBegin import checkLeftAndRightBegin as wzry_logic_check_begin
from wzry.logic.checkChoose import checkChoose as wzry_logic_check_choose
from wzry.logic.checkFighting import checkFighting as wzry_logic_check_fighting
from wzry.logic.checkJiDi import checkWin as wzry_check_win
from wzry.logic.checkScore import checkScore as wzry_check_score

from lol.logic.checkBegin import checkLeftAndRightBegin as lol_logic_check_begin
from lol.logic.checkChoose import checkChoose as lol_logic_check_choose
from lol.logic.checkFightingForZw import checkFighting as zw_lol_logic_check_fighting
from lol.logic.checkFightingForEn import checkFighting as en_lol_logic_check_fighting
from lol.logic.checkJiDi import checkWin as lol_checkWin
from lol.logic.checkScore import checkScore as lol_check_score


from sharedata import dataDef
import numpy

class ConsumerManager(BaseManager):
    pass

def checkGameBegin():

    while True:
        if True:
            if not singletonInstance.task_queue.empty():
                bytesTask = singletonInstance.task_queue.get()
                #time.sleep(2)

                objTask = pickle.loads(bytesTask)
                objResult = dataDef.classImageResult()
                #回传
                objResult.strMatchId = objTask.strMatchId
                objResult.iRound = objTask.iRound
                objResult.strMatchType = objTask.strMatchType
                objResult.strLanguage = objTask.strLanguage

                logging.debug(objTask.strScanFile)

                if objTask.imageDataType == 0:
                    imageOpenCvData = cv2.imread(objTask.strScanFile, cv2.IMREAD_COLOR)
                    logging.debug(objTask.strScanFile)
                elif objTask.imageDataType == 1:
                    imageOpenCvData = objTask.imageOpenCvData
                elif objTask.imageDataType == 2:
                    nparr = numpy.asarray(bytearray(objTask.imageRawData), dtype=numpy.uint8)
                    try:
                        imageOpenCvData = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        #重新resize
                        imageOpenCvData = cv2.resize(imageOpenCvData, (1920, 1080), interpolation=cv2.INTER_CUBIC)
                    except Exception as e:
                        logging.debug(repr(e))
                else:
                    #TODO log error
                    continue

                if objTask.strMatchType == "kog":
                    checkLeftAndRightBegin = wzry_logic_check_begin
                    checkChoose = wzry_logic_check_choose
                    checkFighting = wzry_logic_check_fighting
                    checkWin = wzry_check_win
                    checkScore = wzry_check_score
                elif objTask.strMatchType == "lol" and objTask.strLanguage == "cn":
                    checkLeftAndRightBegin = lol_logic_check_begin
                    checkChoose = lol_logic_check_choose
                    checkFighting = zw_lol_logic_check_fighting
                    checkWin = lol_checkWin
                    checkScore = lol_check_score
                elif objTask.strMatchType == "lol" and objTask.strLanguage == "en":
                    checkLeftAndRightBegin = lol_logic_check_begin
                    checkChoose = lol_logic_check_choose
                    checkFighting = en_lol_logic_check_fighting
                    checkWin = lol_checkWin
                    checkScore = lol_check_score
                elif objTask.strMatchType == "dota2":
                    continue
                else:
                    #TODO error log
                    print("unknown matchType[{}] and languageType[{}]".format(objTask.matchType,objTask.strLanguage))
                    continue

                if imageOpenCvData is None:
                    if objTask.imageDataType == 0:
                        print("{} cv2 read failed".format(objTask.strScanFile))
                        continue
                    else:
                        print("{} frame video read failed".format(objTask.indexFrame))
                        continue

                if objTask.imageForType == "checkBegin":
                    print("checkBegin frame")
                    retFlag = checkLeftAndRightBegin(imageOpenCvData)
                    if retFlag:
                        objResult.result = "beginGame"
                    else:
                        objResult.result = ""

                elif objTask.imageForType == "chooseHero":
                    print("choose Hero")
                    retList = checkChoose(imageOpenCvData)
                    if len(retList) < 10:
                        print("choose Hero not enough 10")
                    else:
                        objResult.result = "endChoose"
                        objResult.value = pickle.dumps(retList)
                        print(retList)

                elif objTask.imageForType == "fighting":
                    print("fighting frame")
                    #listJiSha, listTuiTa, listLong = checkFighting.checkFighting(imageOpenCvData, objTask.indexFrame)
                    retDict = checkFighting(imageOpenCvData, objTask.indexFrame,objTask.strMatchType,objTask.strMatchId,objTask.iRound)
                    if "endGameFlag" in retDict:
                        objResult.result = "endGame"
                        objResult.value = str(objTask.indexFrame)
                    elif "replayFlag" in retDict:
                        objResult.result = "replayGame"
                        objResult.value = str(objTask.indexFrame)
                    else:
                        if objResult.strMatchType == "kog":
                            #TODO 加入一帧里面有多个击杀信息和推塔信息,不过应该不会出现这样的字样
                            if "listJiSha" in retDict:
                                listJiSha = retDict["listJiSha"]
                                if len(listJiSha) > 0:
                                    print(listJiSha)
                                    objResult.result = "jisha"
                                    objResult.value = pickle.dumps({"left":listJiSha[0][0],
                                                                   "right":listJiSha[0][2],
                                                                    "des":listJiSha[0][1],
                                                                    "frameIndex":listJiSha[0][3]})

                            if "listTuiTa" in retDict:
                                listTuiTa = retDict["listTuiTa"]
                                if len(listTuiTa) > 0:
                                    print(listTuiTa)
                                    objResult.result = "tuita"
                                    objResult.value = pickle.dumps({"hero": listTuiTa[0][0],
                                                                    "frameIndex": listTuiTa[0][1]})

                            if "listLong" in retDict:
                                listLong = retDict["listLong"]
                                if len(listLong) > 0:
                                    print(listLong)
                                    objResult.result = "dragon"
                                    objResult.value = pickle.dumps({"hero": listLong[0][0],
                                                                    "dragonType": listLong[0][1],
                                                                    "frameIndex": listLong[0][2]})


                        elif objResult.strMatchType == "lol":

                            if "retTenKillName" in retDict:
                                retTenKillName = retDict["retTenKillName"]
                                print(retTenKillName)
                                objResult.result = "lol_tenKill"
                                #objResult.value = retTenKillName
                                objResult.value = pickle.dumps({"team": retTenKillName,
                                                                #以后改到从task的frameindex 里面去读
                                                                "frameIndex": retDict["frameIndex"]})

                            if "retDragonAttName" in retDict:
                                retDragonAttName = retDict["retDragonAttName"]
                                print(retDragonAttName)
                                objResult.result = "lol_dragonAtt"

                                objResult.value = pickle.dumps({"att": retDragonAttName,
                                                                # 以后改到从task的frameindex 里面去读
                                                                "frameIndex": retDict["frameIndex"]})

                            if "retListFirstTower" in retDict:
                                retListFirstTower = retDict["retListFirstTower"]
                                print(retListFirstTower)

                                objResult.result = "lol_firstTower"

                                objResult.value = pickle.dumps({"hero": retListFirstTower[1],
                                                                "team": retListFirstTower[0],
                                                                # 以后改到从task的frameindex 里面去读
                                                                "frameIndex": retDict["realFrameIndex"]})

                            if "retXiaoGuXiangFeng" in retDict:
                                retXiaoGuXiangFeng = retDict["retXiaoGuXiangFeng"]
                                print(retXiaoGuXiangFeng)

                                objResult.result = "lol_xiaGuXianFeng"

                                objResult.value = pickle.dumps({"hero": retXiaoGuXiangFeng,
                                                                # 以后改到从task的frameindex 里面去读
                                                                "frameIndex": retDict["realFrameIndex"]})

                            if "retSmallDragon" in retDict:
                                retSmallDragon = retDict["retSmallDragon"]
                                print(retSmallDragon)

                                objResult.result = "lol_smallDragon"

                                objResult.value = pickle.dumps({"hero": retSmallDragon,
                                                                # 以后改到从task的frameindex 里面去读
                                                                "frameIndex": retDict["realFrameIndex"]})

                            if "retBigDragon" in retDict:
                                retBigDragon = retDict["retBigDragon"]
                                print(retBigDragon)

                                objResult.result = "lol_bigDragon"

                                objResult.value = pickle.dumps({"hero": retBigDragon,
                                                                # 以后改到从task的frameindex 里面去读
                                                                "frameIndex": retDict["realFrameIndex"]})

                            if "retFirstBlood" in retDict:
                                retFirstBlood = retDict["retFirstBlood"]
                                print(retFirstBlood)
                                objResult.result = "lol_firstBlood"
                                objResult.value = pickle.dumps({"hero": retFirstBlood,
                                                                # 以后改到从task的frameindex 里面去读
                                                                "frameIndex": retDict["realFrameIndex"]})

                            if "retFiveKill" in retDict:
                                print(retDict["retFiveKill"])

                                objResult.result = "lol_fiveKill"
                                objResult.value = pickle.dumps({"hero": retDict["retFiveKill"],
                                                                # 以后改到从task的frameindex 里面去读
                                                                "frameIndex": retDict["realFrameIndex"]})

                            if "retGodLike" in retDict:
                                print(retDict["retGodLike"])

                                objResult.result = "lol_godLike"
                                objResult.value = pickle.dumps({"hero": retDict["retGodLike"],
                                                                # 以后改到从task的frameindex 里面去读
                                                                "frameIndex": retDict["realFrameIndex"]})


                elif objTask.imageForType == "checkWin":
                    print("checkWin frame")
                    iRet = checkWin(imageOpenCvData)
                    objResult.result = "winTeam"
                    if iRet == 0:
                        objResult.value = pickle.dumps({"win":"blue","frameIndex":objTask.indexFrame})
                    else:
                        objResult.value = pickle.dumps({"win":"red", "frameIndex":objTask.indexFrame})

                elif objTask.imageForType == "checkScore":
                    print("checkScore frame")
                    dictRet = checkScore(imageOpenCvData)
                    objResult.result = "scores"

                    if len(dictRet) > 0:
                        dictRet["frameIndex"] = objTask.indexFrame
                        objResult.value = pickle.dumps(dictRet)
                    else:
                        dictRet["frameIndex"] = objTask.indexFrame
                        objResult.value = pickle.dumps(dictRet)

                if True:
                    if singletonInstance.result_queue.full():
                        #TODO print()
                        continue
                    else:
                        bytesResult = pickle.dumps(objResult)
                        if not singletonInstance.result_queue.full():
                            #TODO print
                            singletonInstance.result_queue.put(bytesResult)
                        else:
                            #TODO print
                            pass
            else:
                #queue is empty
                time.sleep(0.01)


if __name__ == "__main__":

    # global objShareMgr

    if float(str(sys.version_info[0]) + str(sys.version_info[1])) < 3.4:
        print("Found Python interpreter less 3.4 version not support: %s \n" % sys.version)

    else:

        parse = OptionParser(usage="%prog --rf <runFlag>")

        parse.add_option("--rf", "--runFlag", dest="runFlag", help="debug or release")
        parse.add_option("--p", "--port", dest="port", help="listen port")

        (options, args) = parse.parse_args()

        runFlag = str(options.runFlag)
        procVariable.port = int(options.port)

        if runFlag == "debug":
            procVariable.debug = True


        ConsumerManager.register('get_task_queue')
        ConsumerManager.register('get_result_queue')
        ConsumerManager.register('get_share_dict', dict, DictProxy)
        #ConsumerManager.register('get_kill_frame',Value, ValueProxy)
        #ConsumerManager.register('get_tower_kill_frame', Value, ValueProxy)
        #ConsumerManager.register('get_dragon_kill_frame', Value, ValueProxy)

        #ConsumerManager.register('get_ten_kill', Value, ValueProxy)
        #ConsumerManager.register('first_dragon_att', Value, ValueProxy)
        #ConsumerManager.register('get_checking_list', list, ListProxy)

        singletonInstance.objShareMgr = ConsumerManager(address=('127.0.0.1', procVariable.port), authkey=b'abc')
        singletonInstance.objShareMgr.connect()

        singletonInstance.task_queue = singletonInstance.objShareMgr.get_task_queue()
        singletonInstance.result_queue = singletonInstance.objShareMgr.get_result_queue()
        #singletonInstance.kill_frame_proxy = singletonInstance.objShareMgr.get_kill_frame()
        #singletonInstance.kill_tower_frame_proxy = singletonInstance.objShareMgr.get_tower_kill_frame()
        #singletonInstance.kill_dragon_frame_proxy = singletonInstance.objShareMgr.get_dragon_kill_frame()

        #singletonInstance.first_ten_kill_frame_proxy = singletonInstance.objShareMgr.get_ten_kill()
        #singletonInstance.first_dragon_attr_frame_proxy = singletonInstance.objShareMgr.first_dragon_att()

        #singletonInstance.check_list = singletonInstance.objShareMgr.get_checking_list()

        #Test
        #singletonInstance.check_list.append("1")
        #singletonInstance.check_list = [[-1, 1920, 0, 1080, 0, None] for i in range(9)]
        singletonInstance.share_dict = singletonInstance.objShareMgr.get_share_dict()

        checkGameBegin()



