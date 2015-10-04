from time import time
import cv2
from redis import Redis
import secret_config

redis = Redis()

def snizzle():
    c = []
    ramp_frames = 20
    cam = cv2.VideoCapture(0)
    while True:
        try:
            ret, im = cam.read()
            for i in xrange(ramp_frames):
                ret, im = cam.read()
            im = im[0:480, 320:640]
            imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            ret, thresh = cv2.threshold(imgray,74,255,0)
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,
                    cv2.CHAIN_APPROX_NONE)
            #cv2.drawContours(im, contours, -1,(0,255,0), 3)
            #cv2.imwrite("base" + str(a) + ".jpg", im)
            num = len(contours)
            c.append(num)
            if len(c)>11:
                c.pop(0)
            average = (sum(c)/float(len(c)))
            print "The average is: " + str(average)
            redis.rpush(secret_config.AVERAGE_LIST, average)
        except:
            pass


if __name__ == "__main__":
    snizzle()
