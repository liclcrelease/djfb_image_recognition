import subprocess
import os,sys
import logging
import time
import threading
import pickle
from service.singleton import singletonInstance
from service.logic import scan
from service.dataDefine import cMatchData


def handleMatchBegin(dictParam:dict):
    strMatchId = dictParam["strMatchId"]
    strMatchFrameDir = dictParam["strMatchFrameDir"]
    strTeamAName = dictParam.get("strTeamAName","")
    strTeamBName = dictParam.get("strTeamBName","")
    strLanguage = dictParam["strLanguage"]
    strMatchType = dictParam["strMatchType"]
    iRound = dictParam["iRound"]

    #查看是否有线程已经存在，处理这个任务
    threadId = singletonInstance.g_scanFileThread.get(strMatchId + str(iRound))

    if threadId is not None:
        while threadId.is_alive():
            #threadId._stop()
            ##threading._shutdown()
            singletonInstance.g_scanFileThreadRunFlag[strMatchId + str(iRound)] = False



    strShareKey = "{}{}_{}".format(strMatchType,strMatchId,iRound)
    dictShareMatchData = singletonInstance.share_dict.get(strShareKey,None)
    if dictShareMatchData is None:
        dictShareMatchData = {}

        dictShareMatchData['kill_frame_proxy'] = 0
        dictShareMatchData['jisha_type'] = 0

        dictShareMatchData['kill_tower_frame_proxy'] = 0
        dictShareMatchData['kill_dragon_frame_proxy'] = 0
        dictShareMatchData['first_ten_kill_frame_proxy'] = 0
        dictShareMatchData['first_dragon_attr_frame_proxy'] = 0
        dictShareMatchData['check_list'] = [[-1, 1920, 0, 1080, 0, None] for i in range(9)]
        singletonInstance.share_dict[strShareKey] = pickle.dumps(dictShareMatchData)

    else:
        logging.debug("already exist match shareKey[{}]".format(strShareKey))
        bytesShareMatchData = singletonInstance.share_dict[strShareKey]
        dictShareMatchData = pickle.loads(bytesShareMatchData)
        dictShareMatchData['kill_frame_proxy'] = 0
        dictShareMatchData['jisha_type'] = 0

        dictShareMatchData['kill_tower_frame_proxy'] = 0
        dictShareMatchData['kill_dragon_frame_proxy'] = 0
        dictShareMatchData['first_ten_kill_frame_proxy'] = 0
        dictShareMatchData['first_dragon_attr_frame_proxy'] = 0
        dictShareMatchData['check_list'] = [[-1, 1920, 0, 1080, 0, None] for i in range(9)]
        singletonInstance.share_dict[strShareKey] = pickle.dumps(dictShareMatchData)
        #return

    objLocalMatchData = singletonInstance.g_matchData.get(strShareKey, None)
    if objLocalMatchData is None:
        objLocalMatchData = cMatchData()
        objLocalMatchData.strMatchType = strMatchType
        objLocalMatchData.strLanguage = strLanguage
        objLocalMatchData.iRound = iRound
        singletonInstance.g_matchData[strShareKey] = objLocalMatchData

    #strFileScanPath = os.path.dirname(__file__) + "/../../fileScan/fileScanSvr.py"
    #pScanFile = subprocess.Popen(["python3",strFileScanPath,"--rf release","--input {}".format(strMatchFrameDir),
    #                              "--mId {}".format(strMatchId),"--mRound {}".format(iRound),"--Language {}".format(strLanguage)])

    #time.sleep(0.1)
    #ret = pScanFile.poll()
    #if ret <= 0:
    #    print("open scan file match[{}]".format(strMatchId))
    #    return

    #开线程去做
    singletonInstance.g_scanFileThreadRunFlag[strMatchId + str(iRound)] = True
    resultThread = threading.Thread(name="result", target=scan.scanFile, args=(strMatchFrameDir,strMatchType,strMatchId,iRound))
    singletonInstance.g_scanFileThread[strMatchId+str(iRound)] = resultThread

    resultThread.start()
    time.sleep(0.1)
    if not resultThread.is_alive():
        logging.debug("open scan file match[{}]".format(strMatchId))
        return

