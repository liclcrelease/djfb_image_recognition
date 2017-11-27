
class classImageTask():
    def __init__(self):
        self.imageForType = ""      #"checkBegin" "chooseHero" "fighting" "end"
        self.imageOpenCvData = None
        self.imageRawData = None
        self.imageDataType = 0      #0 使用pic，1 scanfile 加载的图片 向量, 2 直接发的图片的raw
        self.strScanFile = ""
        self.indexFrame = 0
        self.strMatchType = "" #kog,lol,dota2
        self.strMatchId = ""
        self.strLanguage = "" #cn,en,korean
        self.iRound = 0

class classImageResult():
    def __init__(self):
        self.result = ""            #"beginGame" "endChoose" "endGame" "newFighting"
        self.value = ""
        self.strMatchId = ""        #透传
        self.iRound = 0             #透传
        self.strMatchType = ""      #透传
