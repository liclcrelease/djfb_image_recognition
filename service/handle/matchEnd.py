from service.singleton import singletonInstance

def handleMatchEnd(dictParam:dict):
    strMatchId = dictParam["strMatchId"]
    iRound = dictParam["iRound"]

    threadId =  singletonInstance.g_scanFileThread.get(strMatchId + str(iRound))
    if threadId is not None:
        if threadId.is_alive():
            threadId._stop()
