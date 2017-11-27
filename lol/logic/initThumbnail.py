import os
import cv2
from ctypes import c_int,cdll

#dll模块
dll_object = cdll.LoadLibrary('../lol/lol.dll')
matchtemplate = dll_object.matchtemplate


#左右两边的上面图片，用来确定是否在比赛中
left_head=cv2.imread('../lol/head/left_head.png',cv2.IMREAD_COLOR)
right_head=cv2.imread('../lol/head/right_head.png',cv2.IMREAD_COLOR)
middle_head = cv2.imread('../lol/head/middle.jpg',cv2.IMREAD_COLOR)
middle_black_head = cv2.imread('../lol/head/middle_black.jpg',cv2.IMREAD_COLOR)

heroes_left = {}
for i in os.listdir('../lol/heroes_thumbnail_left'):
    heroes_left[i] = cv2.imread('../lol/heroes_thumbnail_left/' + i, cv2.IMREAD_COLOR)

heroes_right = {}
for i in os.listdir('../lol/heroes_thumbnail_right'):
    heroes_right[i] = cv2.imread('../lol/heroes_thumbnail_right/' + i, cv2.IMREAD_COLOR)



#待匹配图片名称和矩形框
en_all_pic_list=[['blue10.png',[25,62,892,935]],
['red10.png',[25,62,990,1031]],
['shuilong.png',[105,123,116,199]],
['huolong.png',[105,123,116,199]],
['tulong.png',[105,123,116,199]],
['yunlong.png',[105,123,116,199]],
['yuangulong.png',[105,123,116,199]],
['sansha.png',[225,270,813,1103]],
['sisha.png',[225,270,780,1137]],
['yixue.png',[225,270,813,1103]],
['chaoshen.png',[225,270,859,1268]],
['xiaguxianfeng.png',[230,265,755,1320]],
['1long.png',[225,270,815,1260]],
['dalong.png',[225,265,799,1285]],
['yita.png',[228,265,785,1301]]
]


#待匹配图片名称和矩形框
zw_all_pic_list=[['blue10.png',[25,62,892,935]],
['red10.png',[25,62,990,1031]],
['shuilong.png',[103,123,124,157]],
['huolong.png',[103,123,124,157]],
['tulong.png',[103,123,124,157]],
['yunlong.png',[103,123,124,157]],
['yuangulong.png',[103,123,124,157]],
['sansha.png',[222,268,900,1017]],
['sisha.png',[222,268,900,1017]],
['wusha.png',[218,272,892,1024]],
['yixue.png',[222,265,868,1052]],
['chaoshen.png',[225,270,851,1240]],
['xiaguxianfeng.png',[226,264,806,1235]],
['diyitiaolong.png',[226,264,852,1210]],
['nashinanjue.png',[226,264,817,1245]],
['yita.png',[226,264,805,1165]]
]



#提示文字的图片名称和矩形框
en_word_list=[['sansha.png',[225,270,813,1103]],
['sisha.png',[225,270,780,1137]],
['yixue.png',[225,270,813,1103]],
['chaoshen.png',[225,270,859,1268]],
['xiaguxianfeng.png',[230,265,755,1320]],
['1long.png',[225,270,815,1260]],
['dalong.png',[225,265,799,1285]],
['yita.png',[228,265,785,1301]]]


#提示文字的图片名称和矩形框
zw_word_list=[['sansha.png',[222,268,900,1017]],
['sisha.png',[222,268,900,1017]],
['wusha.png',[218,272,892,1024]],
['yixue.png',[222,265,868,1052]],
['chaoshen.png',[225,270,851,1240]],
['xiaguxianfeng.png',[226,264,806,1235]],
['diyitiaolong.png',[226,264,852,1210]],
['nashinanjue.png',[226,264,817,1245]],
['yita.png',[226,264,805,1165]]]


#所有提示文字的图片名称
zw_wordname_list=list(x[0] for x in zw_word_list)
en_wordname_list=list(x[0] for x in en_word_list)




#三杀，四杀，超神的杀人头像和被杀头像和文字的横坐标差值
zw_hero_word_x_diff=[[69,233],[74,239],[],[],[0,208]]
#三杀，四杀，超神的杀人头像和被杀头像和文字的横坐标差值
en_hero_word_x_diff=[[67,306],[70,375],[],[0,228]]

#判断一塔是蓝队拿还是红队拿
zw_yita_list=[['yita_blue.png',None],['yita_red.png',None]]
en_yita_list=[['yita_blue.png',None],['yita_red.png',None]]

#55*55的英雄头像
heroes_55 = []
for i in os.listdir('../lol/heroes_thumbnail_55'):
    heroes_55.append((cv2.imread('../lol/heroes_thumbnail_55/' + i, cv2.IMREAD_COLOR), i))

#65*65的英雄头像
heroes_65 = []
for i in os.listdir('../lol/heroes_thumbnail_65'):
    heroes_65.append((cv2.imread('../lol/heroes_thumbnail_65/' + i, cv2.IMREAD_COLOR), i))


zw_word_dic={}
for i in zw_word_list:
    zw_word_dic[i[0]]=i

en_word_dic={}
for i in en_word_list:
    en_word_dic[i[0]]=i


#带文字提示的图片识别方法：
#取文字的所有像素点和待匹配图片中的文字的所有像素点比较
#占比越大，越匹配
#下面几行代码，保存示例图片的文字所有像素点到c数组里，准备传到c++ dll里计算结果
for i in zw_word_list:
    i.append([])
    temp_pic=cv2.imread('../lol/pic_zwb_new/'+i[0],cv2.IMREAD_COLOR)
    for j in range(temp_pic.shape[0]):
        for k in range(temp_pic.shape[1]):
            if temp_pic[j,k].any():
                i[2].extend([j,k])
    i.append((c_int*len(i[2]))())
    for j in range(len(i[2])):
        i[3][j]=i[2][j]
    i.append(temp_pic.shape)

for i in en_word_list:
    i.append([])
    temp_pic=cv2.imread('../lol/pic_new/'+i[0],cv2.IMREAD_COLOR)
    for j in range(temp_pic.shape[0]):
        for k in range(temp_pic.shape[1]):
            if temp_pic[j,k].any():
                i[2].extend([j,k])
    i.append((c_int*len(i[2]))())
    for j in range(len(i[2])):
        i[3][j]=i[2][j]
    i.append(temp_pic.shape)

#处理红队蓝队的文字字样
for i in en_yita_list:
    i.append([])
    temp_pic = cv2.imread('../lol/pic_new/' + i[0], cv2.IMREAD_COLOR)
    for j in range(temp_pic.shape[0]):
        for k in range(temp_pic.shape[1]):
            if temp_pic[j, k].any():
                i[2].extend([j, k])

    i.append((c_int * len(i[2]))())
    for j in range(len(i[2])):
        i[3][j] = i[2][j]
    i.append(temp_pic.shape)


#处理红队蓝队的文字字样
for i in zw_yita_list:
    i.append([])
    temp_pic = cv2.imread('../lol/pic_zwb_new/' + i[0], cv2.IMREAD_COLOR)
    for j in range(temp_pic.shape[0]):
        for k in range(temp_pic.shape[1]):
            if temp_pic[j, k].any():
                i[2].extend([j, k])

    i.append((c_int * len(i[2]))())
    for j in range(len(i[2])):
        i[3][j] = i[2][j]
    i.append(temp_pic.shape)



red=[[224,54,53]]
blue=[[110,250,254],[8,146,200]]


left_rentou = [19, 67, 887, 940]
right_rentou = [19, 67, 985, 1036]
left_tower = [18, 57, 668, 707]
right_tower = [18, 57, 1247, 1292]

bifen_new_left = []
for i in os.listdir("../lol/bifen_new_left"):
    num_pic = cv2.imread('../lol/bifen_new_left/' + i)
    bifen_new_left.append([i,num_pic])

bifen_new_right = []
for i in os.listdir("../lol/bifen_new_right"):
    num_pic = cv2.imread('../lol/bifen_new_right/' + i)
    bifen_new_right.append([i,num_pic])

bifen_new_left_small = []
for i in os.listdir("../lol/bifen_new_left_small"):
    num_pic = cv2.imread('../lol/bifen_new_left_small/' + i)
    bifen_new_left_small.append([i,num_pic])

bifen_new_right_small = []
for i in os.listdir("../lol/bifen_new_right_small"):
    num_pic = cv2.imread('../lol/bifen_new_right_small/' + i)
    bifen_new_right_small.append([i,num_pic])