"""streamgraph.py

solution strategy:
--find length of yellow part of the image, calibrate to depth
-- ???
--profit

implement as:
--convert image to hsv
--choose a color and threshold range
--create bitmap of pixels within color threshold
--find area as fraction of maximum ruler
--measure ruler by hand in image editor to get calibration
--convert area to calibrated depth  
--create time series of depth, graph it

color sample for yellow ruler in image CDY_0450.JPG is
#DE9D33, or hsv:37,197,222

fixme:
do edge detection one the contour with the largest height
depth is the compliment of the length of ruler visible WRT max visible ruler :)
make mask from clean image with max ruler showing...
"""
import os
import datetime as dt
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image
from PIL import ExifTags

def extractHoughLine(line):
    for rho,theta in line:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
    return (x0, y0, x1, y1, x2, y2)

def showme(image, imagesize=(1024, 768)):
    resizedImage = cv2.resize(image, imagesize)
    cv2.namedWindow('Display Window') #flags=0 for resizeable window
    cv2.imshow('Display Window',resizedImage)
    cv2.waitKey(0)
times = []
contour_height = []
tseries = []
for file in os.listdir('./images'):
    try:
        image = Image.open('./images/'+file)
        exif_data = image._getexif()
        exif = {
            ExifTags.TAGS[k]: v
            for k, v in image._getexif().items()
            if k in ExifTags.TAGS
        }
        image = cv2.imread('./images/'+file, cv2.CV_LOAD_IMAGE_COLOR)
    except:
        print "failed to read: "
        print file
        continue
    hsv = cv2.cvtColor(image, cv2.cv.CV_BGR2HSV)
    cthresh  = cv2.inRange(hsv, (20, 100, 160), (35, 255, 255))
    drawing = np.zeros(cthresh.shape,np.uint8) # Image to draw the contours
    edges = cv2.Canny(cthresh,50,150,apertureSize = 3)
    lines = cv2.HoughLines(edges,1,np.pi/180,255)
    colorimage = cv2.cvtColor(cthresh, cv2.COLOR_GRAY2BGR)
    
    contours,hierarchy = cv2.findContours(cthresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    # for cnt in contours:
    #     color = np.random.randint(0,255,(3)).tolist()  # Select a random color
    #     cv2.drawContours(drawing,[cnt],0,[255, 255, 255],-1)    
    contours = sorted(contours, key=cv2.contourArea)
    largest = contours[-1]
    # height of largest contour
    contour_height.append(int(max(largest[:,:,1])-min(largest[:,:,1])))
#     t =  dt.datetime.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
    times.append(dt.datetime.strptime(exif['DateTimeOriginal'],'%Y:%m:%d %H:%M:%S'))
#     tseries.append([depth, t])
    
    cv2.drawContours(colorimage,[contours[-1]],0,[255, 0, 255],-1)
    
    if lines != None:
        for l in lines:
            (x0, y0, x1, y1, x2, y2) = extractHoughLine(l) # what is p0??
            cv2.line(colorimage,(x1,y1),(x2,y2),(63,255,0),5)

    showme(colorimage)

fig, ax = plt.subplots()
ax.plot(times, contour_height, 'go')
fig.autofmt_xdate()
plt.show()
