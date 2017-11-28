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


def normalPost(matchType,matchId,round,finishTeam, playType,sResultImg):

    dictPost = {}
    dictPost["sGameType"] = matchType
    dictPost["iMatchId"] = int(matchId)
    dictPost["iRoundIndex"] = int(round)
    dictPost["sPlayType"] = playType
    dictPost["iFinishTeam"] = 0 if finishTeam == "blue" else 1
    dictPost["sResultImg"] = str(sResultImg).zfill(7)

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def normalPostWithParam(matchType,matchId,round,finishTeam, playType,sResultImg,sParam):

    dictPost = {}
    dictPost["sGameType"] = matchType
    dictPost["iMatchId"] = int(matchId)
    dictPost["iRoundIndex"] = int(round)
    dictPost["sPlayType"] = playType
    dictPost["iFinishTeam"] = 0 if finishTeam == "blue" else 1
    dictPost["sResultImg"] = str(sResultImg).zfill(7)
    dictPost["sParameter"] = sParam

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def normalPostWithoutTeam(matchType, matchId, round, playType,sResultImg):
    dictPost = {}
    dictPost["sGameType"] = matchType
    dictPost["iMatchId"] = int(matchId)
    dictPost["iRoundIndex"] = int(round)
    dictPost["sPlayType"] = playType
    dictPost["sResultImg"] = str(sResultImg).zfill(7)

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def normalPostWithParamWithoutTeam(matchType, matchId, round, playType,sParam,sResultImg):
    dictPost = {}
    dictPost["sGameType"] = matchType
    dictPost["iMatchId"] = int(matchId)
    dictPost["iRoundIndex"] = int(round)
    dictPost["sPlayType"] = playType
    dictPost["sParameter"] = sParam
    dictPost["sResultImg"] = str(sResultImg).zfill(7)

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def dragonType(matchType, matchId, round, playType, dragonType,sResultImg):

    dictPost = {}
    dictPost["sGameType"] = matchType
    dictPost["iMatchId"] = int(matchId)
    dictPost["iRoundIndex"] = int(round)
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


def comboKill(matchType, matchId, round, finishTeam, playType):
    dictPost = {}
    dictPost["sGameType"] = matchType
    dictPost["iMatchId"] = int(matchId)
    dictPost["iRoundIndex"] = int(round)
    dictPost["sPlayType"] = playType
    dictPost["iFinishTeam"] = 0 if finishTeam == "blue" else 1

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def resultKills(matchType, matchId, round, finishTeam, playType,killNum):

    dictPost = {}
    dictPost["sGameType"] = matchType
    dictPost["iMatchId"] = int(matchId)
    dictPost["iRoundIndex"] = int(round)
    dictPost["sPlayType"] = playType
    dictPost["sParameter"] = str(killNum)
    dictPost["iFinishTeam"] = 0 if finishTeam == "blue" else 1

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def towers(matchType, matchId, round, finishTeam, playType,towerNum):

    dictPost = {}
    dictPost["sGameType"] = matchType
    dictPost["iMatchId"] = int(matchId)
    dictPost["iRoundIndex"] = int(round)
    dictPost["sPlayType"] = playType
    dictPost["sParameter"] = str(towerNum)
    dictPost["iFinishTeam"] = 0 if finishTeam == "blue" else 1

    singletonInstance.g_postQueue.put(json.dumps(dictPost))

def roundEnd(matchType, matchId, round):
    dictPost = {}
    dictPost["sGameType"] = matchType
    dictPost["iMatchId"] = int(matchId)
    dictPost["iRoundIndex"] = int(round)

    singletonInstance.g_postQueue.put(json.dumps(dictPost))