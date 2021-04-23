import cv2

img=cv2.imread('./data/chart/day/up/aaaaaBTC_20.jpg')

while True:
    cv2.imshow('asd',img)
    if cv2.waitKey(10)==27:
        break