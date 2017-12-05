from service.singleton import singletonInstance

def handleMatchEnd(dictParam:dict):
    strMatchId = dictParam["strMatchId"]
    iRound = dictParam["iRound"]

    threadId =  singletonInstance.g_scanFileThread.get(strMatchId + str(iRound))
    if threadId is not None:
        while threadId.is_alive():
            singletonInstance.g_scanFileThreadRunFlag[strMatchId + str(iRound)] = False
