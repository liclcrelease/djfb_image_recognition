import requests
import json
import logging
from service.singleton import singletonInstance
from service.serviceConfig import postUrlDebug,postUrlRelease,postStatusUrlDebug,postStatusUrlRelease
from service.proc import procVariable

def postResult():

    while True:
        bytesJsonPost = singletonInstance.g_postQueue.get()
        #dictPost = json.loads(bytesJsonPost)
        dictHeader = {"Accept":"text/html","content-Type":"application/x-www-form-urlencoded"}

        if procVariable.debug:
            postUrl = postUrlDebug

        else:
            postUrl = postUrlRelease
        #print(json.dumps(dictPost))
        ret = requests.post(postUrl, data={"json": bytesJsonPost}, timeout=1, headers=dictHeader)
        logging.debug(bytesJsonPost)
        if ret.status_code == 200:
            logging.debug(ret.text)
        else:
            logging.debug("post url[{}] code[{}]".format(postUrl,ret))

def postStatus():
    while True:
        bytesJsonPost = singletonInstance.g_statusQueue.get()

        dictHeader = {"Accept":"text/html","content-Type":"application/x-www-form-urlencoded"}

        if procVariable.debug:
            postUrl = postStatusUrlDebug
        else:
            postUrl = postStatusUrlRelease

        #print(json.dumps(dictPost))
        ret = requests.post(postUrl, data={"json": bytesJsonPost}, timeout=1, headers=dictHeader)
        logging.debug(bytesJsonPost)
        if ret.status_code == 200:
            logging.debug(ret.text)
        else:
            logging.debug("post url[{}] code[{}]".format(postUrl,ret))


def normalPost(objResult,finishTeam, playType,sResultImg):
    dictPost = {}
    dictPost["sGameType"] = objResult.strMatchType
    dictPost["iMatchId"] = int(objResult.strMatchId)
    dictPost["iRoundIndex"] = int(objResult.iRound)
    dictPost["sResultLanguage"] = objResult.strLanguage
    dictPost["sPlayType"] = playType
    if finishTeam == "blue":
        dictPost["iFinishTeam"] = 0
    elif finishTeam == "red":
        dictPost["iFinishTeam"] = 1
    else:
        dictPost["iFinishTeam"] = 2

    dictPost["sResultImg"] = str(sResultImg).zfill(7)

    print("post {}".format(dictPost))

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def normalPostWithParam(objResult,finishTeam, playType,sResultImg,sParam):

    dictPost = {}
    dictPost["sGameType"] = objResult.strMatchType
    dictPost["iMatchId"] = int(objResult.strMatchId)
    dictPost["iRoundIndex"] = int(objResult.iRound)
    dictPost["sResultLanguage"] = objResult.strLanguage
    dictPost["sPlayType"] = playType
    dictPost["iFinishTeam"] = 0 if finishTeam == "blue" else 1
    dictPost["sResultImg"] = str(sResultImg).zfill(7)
    dictPost["sParameter"] = sParam

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def normalPostWithoutTeam(matchType, matchId, round, strLanguage,playType,sResultImg):
    dictPost = {}
    dictPost["sGameType"] = matchType
    dictPost["iMatchId"] = int(matchId)
    dictPost["iRoundIndex"] = int(round)
    dictPost["sPlayType"] = playType
    dictPost["sResultImg"] = str(sResultImg).zfill(7)

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def normalPostWithParamWithoutTeam(objResult,playType,sParam,sResultImg):
    dictPost = {}
    dictPost["sGameType"] = objResult.strMatchType
    dictPost["iMatchId"] = int(objResult.strMatchId)
    dictPost["iRoundIndex"] = int(objResult.iRound)
    dictPost["sResultLanguage"] = objResult.strLanguage
    dictPost["sPlayType"] = playType
    dictPost["sParameter"] = sParam
    dictPost["sResultImg"] = str(sResultImg).zfill(7)

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def dragonType(objResult, playType, dragonType,sResultImg):

    dictPost = {}
    dictPost["sGameType"] = objResult.strMatchType
    dictPost["iMatchId"] = int(objResult.strMatchId)
    dictPost["iRoundIndex"] = int(objResult.iRound)
    dictPost["sResultLanguage"] = objResult.strLanguage
    dictPost["sPlayType"] = playType
    dictPost["sResultImg"] = str(sResultImg).zfill(7)
    if dragonType == "tulong":
        dictPost["sParameter"] = '1'
    elif dragonType == "shuilong":
        dictPost["sParameter"] = '2'
    elif dragonType == "fenglong":
        dictPost["sParameter"] = '3'
    elif dragonType == "huolong":
        dictPost["sParameter"] = '4'


    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def riverBuffType():
    pass


def status(objMatch,frame_id:int):
    dictPost = {}
    dictPost["sGameType"] = objMatch.strMatchType
    dictPost["iMatchId"] = int(objMatch.strMatchId)
    dictPost["iRoundIndex"] = int(objMatch.iRound)
    dictPost["sResultLanguage"] = objMatch.strLanguage
    dictPost["iRecStatus"] = 0
    dictPost["sFrameId"] = str(frame_id).zfill(7)

    singletonInstance.g_postQueue.put(json.dumps(dictPost))