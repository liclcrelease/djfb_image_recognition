import os
import cv2


#英雄头像
heroes=[]

for i in os.listdir('../wzry/heroes_thumbnail_1080'):
    heroes.append((cv2.imread('../wzry/heroes_thumbnail_1080/'+i,cv2.IMREAD_COLOR),i))

a=[[4,376,61,433],[4,470,61,527],[4,565,61,622],[4,659,61,716],[4,754,61,811]]
b=[[1859,376,1916,433],[1859,470,1916,527],[1859,565,1916,622],[1859,659,1916,716],[1859,754,1916,811]]
matchArray = a + b



#开局得左右图标
leftPic = cv2.imread('../wzry/begin_thumbnail_1080/pic1.png',cv2.IMREAD_COLOR)
rightPic = cv2.imread('../wzry/begin_thumbnail_1080/pic2.png',cv2.IMREAD_COLOR)

sPic = cv2.imread('../wzry/begin_thumbnail_1080/s.png',cv2.IMREAD_COLOR)
s_smallPic = cv2.imread('../wzry/begin_thumbnail_1080/s_small.png',cv2.IMREAD_COLOR)


jisha=[]

#各个击杀信息的矩形框
jisha_a=[(595,135,760,175),(630,135,721,175),(637,135,714,175),(578,134,772,180)]
jisha_b=[]
for i in jisha_a:
    jisha_b.append((int(i[0]/750*1080),int(i[1]/750*1080),int(i[2]/750*1080),int(i[3]/750*1080)))
jisha_b.append((858,197,1083,253))
#print(b)

for i in os.listdir('../wzry/jisha'):
    #t:[击杀图像，击杀类别，矩形框】
    t=[cv2.imread('../wzry/jisha/'+i,cv2.IMREAD_COLOR)]
    t.append(i)
    if i not in ('diyidixue.png','siliansha.png','wuliansha.png','zhongjie.png','jisha.png','zhongjie2.png'):
        t.append(jisha_b[0])
    elif i in ('zhongjie.png','zhongjie2.png'):
        t.append(jisha_b[1])
    elif i == 'jisha.png':
        t.append(jisha_b[2])
    elif i == 'diyidixue.png':
        t.append(jisha_b[4])
    else:
        t.append(jisha_b[3])
    jisha.append(t)

#print(len(jisha))

#heroes里是处理过的英雄头像和小兵头像信息，取上半部分，并把背景变成黑色
jishaheroes=[]
for i in os.listdir('../wzry/heroes_thumbnail_jisha_1080'):
    jishaheroes.append((cv2.imread('../wzry/heroes_thumbnail_jisha_1080/'+i,cv2.IMREAD_COLOR)[:74],i))
xiaobing=cv2.imread('../wzry/xiaobing/xiaobingfangyuta.jpg',cv2.IMREAD_COLOR)[104:147,381:440]
xiaobing=cv2.resize(xiaobing,(99,74),interpolation=cv2.INTER_CUBIC)
for i1 in range(74):
    for j1 in range(99):
        if (i1-49)**2+(j1-49)**2>49*49:
            xiaobing[i1,j1]=0
jishaheroes.append((xiaobing,'xiaobing.png'))



diFang=cv2.imread('../wzry/fangyuta/fangyuta_difang.png',cv2.IMREAD_COLOR)[200:253,897:1048]
woFang=cv2.imread('../wzry/fangyuta/fangyuta_wofang.png',cv2.IMREAD_COLOR)[200:253,871:1022]




#im,im2,im3是暴君，主宰，黑暗暴君被击杀的文字信息
baojun=cv2.imread('../wzry/long/baojun_1080.png',cv2.IMREAD_COLOR)[196:253,818:1023]
zhuzai=cv2.imread('../wzry/long/zhuzai_1080.png',cv2.IMREAD_COLOR)[196:253,818:1023]
heianbaojun=cv2.imread('../wzry/long/heianbaojun.png',cv2.IMREAD_COLOR)[196:253,871:1073]




#提取出的红队水晶和蓝队水晶的rgb值
red=[[211,36,75],[255,255,254],[251,163,150],[255,196,162],[239,64,46],[253,218,233],[220,0,40],[255,213,60]]
blue=[[38,245,255],[13,174,255],[255,252,249],[58,255,251],[94,255,253],[93,230,252]]


#击杀的个数
left_kill = []
for var in range(0,9):
    left_kill.append([var,cv2.imread('../wzry/bifen_left/{}.jpg'.format(var),cv2.IMREAD_COLOR)])

right_kill = []
for var in range(0,9):
    right_kill.append([var,cv2.imread('../wzry/bifen_right/{}.jpg'.format(var),cv2.IMREAD_COLOR)])

