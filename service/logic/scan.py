import time
import pickle
import threading
import logging
from sharedata import dataDef
from service import serviceConfig
from service.singleton import singletonInstance

def scanFile(dirPath:str,matchType:str,matchId:str,iRound:int):

    #global intScanFileIndex
    #global intCheckWinIndex
    #global intEndGameIndex

    intTryFileNotFoundNum = 0
    intSkipNum = 0
    while singletonInstance.g_scanFileThreadRunFlag[matchId + str(iRound)]:

        strShareKey = "{}{}_{}".format(matchType, matchId, iRound)
        objMatchData = singletonInstance.g_matchData.get(strShareKey, None)
        if objMatchData is None:
            logging.debug("match data is not found [{}]".format(matchId))
            return

        if objMatchData.getGameState() == "checkWin":
            strScanFile = "{}\{}.jpg".format(dirPath, str(objMatchData.getCheckWinIndex()).zfill(7))
        elif objMatchData.getGameState() == "checkScore":
            strScanFile = "{}\{}.jpg".format(dirPath, str(objMatchData.getCheckScoreIndex()).zfill(7))
        else:
            strScanFile = "{}\{}.jpg".format(dirPath, str(objMatchData.getScanFileIndex()).zfill(7))

        bytesImageRaw = None

        try:
            openImageFile = open(strScanFile, "rb")
            if openImageFile is None:
                time.sleep(1)
                continue
            else:
                bytesImageRaw = openImageFile.read()

        except FileNotFoundError:
            time.sleep(1)
            intTryFileNotFoundNum+=1
            if intTryFileNotFoundNum > 10:
                #尝试跳帧
                objMatchData.addScanFileIndex()
                intTryFileNotFoundNum = 0
                intSkipNum += 1
                if intSkipNum >= 10:
                    logging.debug("skip num more than 10 exit process")
                    #保存到数据库,关闭进程
                    return
            continue

        except Exception as e:
            logging.debug(repr(e))

        objTask = dataDef.classImageTask()
        objTask.imageForType = objMatchData.getGameState()#"fighting"
        objTask.strScanFile = strScanFile
        objTask.strMatchId = matchId

        if objMatchData.getGameState() == "checkWin":
            objTask.indexFrame = objMatchData.getCheckWinIndex()#intCheckWinIndex
        elif objMatchData.getGameState() == "checkScore":
            objTask.indexFrame = objMatchData.getCheckScoreIndex()  # intCheckWinIndex
        else:
            objTask.indexFrame = objMatchData.getScanFileIndex()#intScanFileIndex

        objTask.imageRawData = bytesImageRaw#cv2.imread(strScanFile, cv2.IMREAD_COLOR)
        #print(len(objTask.imageRawData))
        objTask.imageDataType = 2
        objTask.strMatchType = matchType#objMatchData.strMatchType
        objTask.strLanguage  = objMatchData.strLanguage
        objTask.iRound = objMatchData.iRound

        if True:
            if not singletonInstance.task_queue.full():
                #beginTime = time.time()
                singletonInstance.task_queue.put(pickle.dumps(objTask))
                #print(time.time() - beginTime)
                logging.debug("task queue size [{}] [{}] [{}]".format(singletonInstance.task_queue.qsize(), threading.currentThread().getName(), strScanFile))
                if objMatchData.getGameState() == "checkWin":
                    #intCheckWinIndex += 1
                    objMatchData.addCheckWinIndex()
                elif objMatchData.getGameState() == "checkScore":
                    
                    objMatchData.addCheckScoreIndex()
                else:
                    #intScanFileIndex += 1
                    objMatchData.addScanFileIndex()

                if objMatchData.getCheckWinIndex() != 0 and objMatchData.getCheckWinIndex() >= objMatchData.getEndGameIndex():
                    #end the game
                    objMatchData.setCloseImageCheck(True)
                    logging.debug("exit the scan thread shareKey[{}]".format(strShareKey))
                    return

            else:
                #print("task queue full size [{}]".format(singletonInstance.task_queue.qsize()))
                time.sleep(0.01)
                pass