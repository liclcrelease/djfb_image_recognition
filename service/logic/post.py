import requests
import json
from service.singleton import singletonInstance
from service.serviceConfig import postUrl

def postResult():

    while True:
        bytesJsonPost = singletonInstance.g_postQueue.get()
        #dictPost = json.loads(bytesJsonPost)
        dictHeader = {"Accept":"text/html","content-Type":"application/x-www-form-urlencoded"}
        ret = requests.post(postUrl, data={"json":bytesJsonPost},timeout = 1,headers=dictHeader)
        #print(json.dumps(dictPost))
        print(bytesJsonPost)
        if ret.status_code == 200:
            print(ret.text)
        else:
            print("post url[{}] code[{}]".format(postUrl,ret))


def normalPost(objResult,finishTeam, playType,sResultImg):
    dictPost = {}
    dictPost["sGameType"] = objResult.strMatchType
    dictPost["iMatchId"] = int(objResult.strMatchId)
    dictPost["iRoundIndex"] = int(objResult.iRound)
    dictPost["sResultLanguage"] = objResult.strLanguage
    dictPost["sPlayType"] = playType
    dictPost["iFinishTeam"] = 0 if finishTeam == "blue" else 1
    dictPost["sResultImg"] = str(sResultImg).zfill(7)

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

