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

TODO:
do edge detection one the contour with the largest height
make mask from clean image with max ruler showing...

manual calibration by inspection of CDY_0450.JPG from sample set:
	y = 2px = 5.28 ft
	y = 1485px = 0.0 ft
	1483px/63.36in = 23.4px/in
	(1485px-1536px)/(23.4px/in) = -2.18in @ bottom of frame
"""

import os
import datetime
import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import dates
from PIL import Image
from PIL import ExifTags
from operator import itemgetter

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
length_calibration = 23.4 # px/in
offset_calibration = -51 # px elevation @ 0 inches
times = []
calibrated_depths = []
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
        print "failed to read: "+ file
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

    # height of the bottom of the visible part of ruler from bottom of frame
    # equals y size, in pixels, minus largest y co-ord (farthest from top)
    # px      = image height          - lowest px in contour
    height_px = int(np.shape(image)[0]-max(largest[:,:,1]))

    # height in inches
    calibrated_depths.append((height_px+offset_calibration)/length_calibration)
    print file+' '+str(calibrated_depths[-1])[0:5]+' in.@'+exif['DateTimeOriginal']
#     t =  datetime.datetime.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
    times.append(datetime.datetime.strptime(exif['DateTimeOriginal'],'%Y:%m:%d %H:%M:%S'))
#     tseries.append([depth, t])
    
    cv2.drawContours(colorimage,[contours[-1]],0,[255, 0, 255],-1)
    
    if lines != None:
        for l in lines:
            (x0, y0, x1, y1, x2, y2) = extractHoughLine(l) # what is p0??
            cv2.line(colorimage,(x1,y1),(x2,y2),(63,255,0),5)

    showme(colorimage)

# sort by date 
times, calibrated_depths = (list(x) for x in zip(*sorted(zip(times, calibrated_depths),key=itemgetter(0))))

fig, ax = plt.subplots()
ax.plot(times, calibrated_depths, 'g-')
hfmt = dates.DateFormatter('%m/%d %H:%M')
ax.xaxis.set_major_formatter(hfmt)
ax.set_ylim(bottom = 0)
plt.subplots_adjust(bottom=.2)
plt.xticks(rotation='vertical')
fig.suptitle('Stream Stage', fontsize=14)
plt.ylabel('Inches', fontsize=12)
fig.autofmt_xdate()
plt.show()
fig.savefig('streamgraph_sample.jpg')
