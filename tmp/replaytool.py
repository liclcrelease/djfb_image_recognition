import cv2


frame = cv2.imread("D:\\tuxiang\\tmp\\s_replay.jpg")

#saveFrame = frame[78:175,120:441] #for zw
saveFrame = frame[74:154,42:379] #for zw


cv2.imwrite("../lol/head/en_replay.jpg",saveFrame)
