from threading import Lock

class cPostData:
    def __init__(self):
        self.strMatchId = ""
        self.iRound = ""
        self.dictData = {}

class cServerData:
    def __init__(self):
        self.cpuAverage = 0


class cMatchData:
    def __init__(self):
        self.closeImageCheck = False
        self.closeImageCheckLock = Lock()

        self.intBlueWin = 0
        self.intRedWin = 0
        self.strGameState = "chooseHero"#"fighting"#"checkBegin"
        #self.strGameState = "fighting"#"checkBegin"


        #self.intScanFileIndex = 20600
        #self.intScanFileIndex = 1
        #self.intScanFileIndex = 7272
        #self.intScanFileIndex = 21050
        #self.intScanFileIndex = 33570
        self.intScanFileIndex = 9092
        self.intBeginCheckNum = 0               #开局检测帧数
        self.intEndCheckNum = 0                 #结束检测帧数
        self.intEndGameIndex = 0                #结束帧索引
        self.intCheckWinIndex = 0               #检测输赢开始索引
        self.intCheckScoreIndex = 0             #检测比分索引

        self.strMatchType = ""
        self.strLanguage = ""
        self.iRound = 0

        self.arrayBlueTeam = []
        self.arrayRedTeam = []


        #wzry
        self.intKillHeroFrameIndex = 0
        self.strKillHeroLeft = ""
        self.strKillHeroRight = ""


        self.intBlueDestroyTowerNum = 0
        self.intRedDestroyTowerNum = 0


        self.intLastDestroyTowerTimestamp = 0  #判断连续帧用
        self.intLastDestroyTowerFrameIndex = 0 #判断连续帧用
        self.strLastDestroyHero = ""           #判断连续帧用


        self.intBlueKillBaoJunNum = 0
        self.intBlueKillZhuZaiNum = 0

        self.intRedKillBaoJunNum = 0
        self.intRedKillZhuZaiNum = 0

        self.intLastKillBaoJunTimestamp = 0     # 判断连续帧用
        self.strLastKillBaoJunHero = ""         # 判断连续帧用
        self.intLastKillBaoJunFrameIndex = 0    # 判断连续帧用

        self.intLastKillZhuZaiTimestamp = 0
        self.strLastKillZhuZaiHero = ""         # 判断连续帧用
        self.intLastKillZhuZaiFrameIndex = 0    # 判断连续帧用


        #comm
        self.intBlueKill = 0
        self.intRedKill = 0
        self.intBlueDestroyTower = 0
        self.intRedDestroyTower = 0

        self.intBlueScore = 0
        self.intRedScore = 0

        #lol
        self.intSmallDragonFrame = 0
        self.intBigDragonFrame = 0

        self.strKillSmallDragonHero = ""
        self.strKillBigDragonHero = ""

        self.intLastKillSmallDragonTimestamp = 0
        self.intLastKillBigDragonTimestamp = 0

        self.intKillSmallDragonNum = 0
        self.intKillBigDragonNum = 0

        self.strFirstDragonAtt = ""


    def setCloseImageCheck(self,flag: bool):
        with self.closeImageCheckLock:
            self.closeImageCheck = flag

    def getCloseImageCheck(self):
        with self.closeImageCheckLock:
            return self.closeImageCheck

    def addBeginCheckNum(self):
        self.intBeginCheckNum += 1
        return self.intBeginCheckNum

    def addEndCheckNum(self):
        self.intEndCheckNum += 1
        return self.intEndCheckNum

    def resetEndCheckNum(self):
        self.intEndCheckNum = 0

    def setCheckWinIndex(self,index: int):
        self.intCheckWinIndex = index

    def setEndGameIndex(self,index: int):
        self.intEndGameIndex = index

    def getEndGameIndex(self):
        return self.intEndGameIndex

    def getCheckWinIndex(self):
        return self.intCheckWinIndex
    def addCheckWinIndex(self):
        self.intCheckWinIndex+=1

    def getScanFileIndex(self):
        return self.intScanFileIndex

    def addScanFileIndex(self):
        self.intScanFileIndex += 1

    def addBlueWin(self):
        self.intBlueWin += 1

    def addRedWin(self):
        self.intRedWin += 1

    def getWinNum(self):
        return self.intBlueWin, self.intRedWin

    def setGameState(self,state: str):
        self.strGameState = state
        #print("set GameState[{}]".format(state))

    def getGameState(self):
        return self.strGameState

    def setCheckScoreIndex(self,index:int):
        self.intCheckScoreIndex = index

    def getCheckScoreIndex(self):
        return self.intCheckScoreIndex
    def addCheckScoreIndex(self):
        self.intCheckScoreIndex+=1
