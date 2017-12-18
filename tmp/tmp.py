import cv2
import numpy

"""

frame = cv2.imread("D:\\tmp\\test6\\0039589.jpg",cv2.IMREAD_GRAYSCALE)
#dstframe = cv2.imread("D:\\tmp\\test6\\6.jpg",cv2.IMREAD_COLOR)
#tmp= frame[:,:]
frame = frame[19:67, 990:1032]

element = cv2.getStructuringElement(cv2.MORPH_CROSS,(2,2))

#test = cv2.morphologyEx(frame,cv2.MORPH_OPEN,element)
#test = cv2.resize(test,(500,500))
#cv2.imshow("test",test)

test = cv2.dilate(frame,element)#,borderType=cv2.BORDER_CONSTANT,borderValue=100)
#test = cv2.morphologyEx(test,cv2.MORPH_OPEN,element)
#test = cv2.resize(test,(500,500))
cv2.imshow("test",test)
#erode = cv2.erode(frame, element)
#after = cv2.resize(test,(100,100))
#cv2.imshow("test",after)
#cv2.imshow("erode",erode)
#result = cv2.absdiff(test,erode)
#cv2.imshow("result",result)


#上面得到的结果是灰度图，将其二值化以便更清楚的观察结果
#retval, result = cv2.threshold(result, 40, 255, cv2.THRESH_BINARY)
#反色，即对二值图每个像素取反
#result = cv2.bitwise_not(result)
#cv2.imshow("result",retval)
"""
import numpy as np



element = cv2.getStructuringElement(cv2.MORPH_CROSS,(2,2))
frame = cv2.imread("E:\\tmp\\lol5\\0000225.jpg",cv2.IMREAD_COLOR)
#frame = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)


#frame = frame[19:67, 990:1032]
frame = frame[18:(18+23), 1260:1283]
#cv2.rectangle(frame,)
frame = cv2.resize(frame,(280,280))
cv2.imshow("test",frame)
frame,g,r = cv2.split(frame)
cv2.imshow("testb",frame)
cv2.imshow("testg",g)
cv2.imshow("testr",r)

#frame = test(frame)
#cv2.imshow("testsjflskjd",frame)

#element_1 = cv2.getStructuringElement(cv2.MORPH_CROSS,(2,2))
#frame = cv2.dilate(frame, element_1)
#cv2.imshow("testsdilate",frame)


#horizontalSobelMtx = [[-1,-1,-1],[-1,5,-1],[-1,-1,-1]]
#horizontalSobelMtx = numpy.asanyarray(horizontalSobelMtx, np.float32)

#frame = cv2.filter2D(frame,-1,horizontalSobelMtx)
#cv2.imshow("testsfilter",frame)


#frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, element)
#cv2.imshow("open",frame)


retval, frame = cv2.threshold(frame, 20, 255, cv2.THRESH_BINARY)
retval2, g = cv2.threshold(g, 10, 255, cv2.THRESH_BINARY)
retval3, r = cv2.threshold(r, 70, 255, cv2.THRESH_BINARY)
#retval, frame = cv2.threshold(frame, 111, 255, cv2.THRESH_BINARY)

frame = cv2.bitwise_not(frame)
#frame = cv2.resize(frame,(280,280))
#frame = frame[int(280*0.15):int(280*0.85),int(280*0.15):int(280*0.85)]
frame = cv2.resize(frame,(280,280))
frame[0:int(280*0.15),:] = 255
frame[int(280*0.85):,:] = 255

frame[:,0:int(280*0.15)] = 255
frame[:,int(280*0.85):] = 255

#element_1 = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
#frame = cv2.dilate(frame, element_1,iterations=2)
#g = cv2.bitwise_not(g)
g = cv2.resize(g,(280,280))
g = g[int(280*0.15):int(280*0.85),int(280*0.15):int(280*0.85)]
g = cv2.resize(g,(280,280))

r = cv2.bitwise_not(r)
r = cv2.resize(r,(280,280))
r = r[int(280*0.15):int(280*0.85),int(280*0.15):int(280*0.85)]
r = cv2.resize(r,(280,280))



cv2.imshow("resultb",frame)
cv2.imshow("resultg",g)
cv2.imshow("resultr",r)

#frame = cv2.morphologyEx(frame,cv2.MORPH_OPEN,element)
#b,g,r = cv2.split(frame)
#cv2.imshow("resultb",b)
#cv2.imshow("resultg",g)

#cv2.imshow("resultr",frame)

k = cv2.waitKey(0)
if k == 27:  # wait for ESC key to exit
    cv2.destroyAllWindows()
elif k == ord('s'):  # wait for 's' key to save and exit
    cv2.imwrite("D:\\tmp\\test6\\rightkill_1.jpg",frame)
    cv2.destroyAllWindows()
