from service.singleton import singletonInstance
from lib.timehelp import timeHelp
from service.logic import post
import logging
import time
from service import serviceConfig

def timerCheck():

    while True:
        try:
            for var_key,objMatchData in singletonInstance.g_matchData.items():

                if objMatchData.getGameState() == "fighting":
                    #防止已经结束的比赛,又因为这个线程里面的timer 重新设置一次end game
                    if objMatchData.intCheckWinLastTime != 0 and (timeHelp.getNow() - objMatchData.intCheckWinLastTime) > 60:
                        objMatchData.intCheckWinLastTime = 0
                        logging.debug("endGame more than 60s time")
                        objMatchData.setCheckWinIndex(
                            objMatchData.intLastResultFrameIndex - objMatchData.intEndCheckNum - serviceConfig.checkWinFrameNum - serviceConfig.queueSizeEndModify)
                        objMatchData.setEndGameIndex(objMatchData.intLastResultFrameIndex - objMatchData.intEndCheckNum - serviceConfig.queueSizeEndModify)
                        objMatchData.setCheckScoreIndex(
                            objMatchData.intLastResultFrameIndex - objMatchData.intEndCheckNum - serviceConfig.checkScoreFrameNum - serviceConfig.queueSizeEndModify)
                        objMatchData.setGameState("checkScore")

                post.status(objMatchData,objMatchData.intScanFileIndex)

        except Exception as e:
            print(repr(e))

        time.sleep(10)
