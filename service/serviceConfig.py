tempBase = 25 * 15       #25帧 15秒
queueSizeEndModify = 20  #和queue size 有关 修正结束帧数用
checkWinFrameNum = 30 * 1
checkScoreFrameNum = 60
checkEndScoreFrameNum = 25      #最後結束frame 前25鎮，擊殺人頭才顯示，後面25鎮不顯示
postUrlDebug = "http://192.168.1.100:8090/api/fighting/result"
postUrlRelease = "http://172.18.244.218:8090/api/fighting/result"


postStatusUrlDebug = "http://192.168.1.100:8090/api/fighting/recStatusUpdate"
postStatusUrlRelease = "http://172.18.244.218:8090/api/fighting/recStatusUpdate"