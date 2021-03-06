#!/usr/bin/env python3
# MIT License

# Copyright (c) 2017-18 Jetsonhacks

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# Grabs the average coordinates for the contour and then prints them
# todo: add networktables and sorting for filtering

import cv2
import cscore as cs
import numpy as np
import math
import array as arr
# import socket

from networktables import NetworkTables

cam = cv2.VideoCapture(1)
cam2 = cv2.VideoCapture(2)

x = 0
y = 0
xdist = 0
w = 0
h = 0
i = 0
counterr = 0
total = 0
area = 0
xavg = 0
pairs = []

irl_coords = np.array([
    # Left target
    (-5.938, 2.938, 0.0), # top left
    (-4.063, 2.375, 0.0), # top right
    (-5.438, -2.938, 0.0), # bottom left
    (-7.375, -2.500, 0.0), # bottom right

     # Right target
     (3.938, 2.375, 0.0), # top left
     (5.875, 2.875, 0.0), # top right
     (7.313, -2.500, 0.0), # bottom left
     (5.375, -2.938, 0.0) # bottom right
])

# irl_coords = arr.array(
#     # Left target
#     [-5.938, 2.938, 0.0], # top left
#     [-4.063, 2.375, 0.0], # top right
#     [-5.438, -2.938, 0.0], # bottom left
#     [-7.375, -2.500, 0.0], # bottom right
#
#     # Right target
#     [3.938, 2.375, 0.0], # top left
#     [5.875, 2.875, 0.0], # top right
#     [7.313, -2.500, 0.0], # bottom left
#     [5.375, -2.938, 0.0], # bottom right
# )
distortion = np.array([[-0.08188277546240876, 0.2648828543695779, -0.0017486930982830986, 0.004465490753411877, -0.11525824611329834]])
camera_matrix = np.array([[543.8671906643532, 0.0, 322.20900066995284], [0.0, 542.0943784692347, 250.07849777968718], [0.0, 0.0, 1.0]])

camera = cs.CvSource("cvsource", cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 20)
mjpegServer = cs.MjpegServer("httpserver", 8081)
mjpegServer.setSource(camera)

#Comment

# NetworkTables.initialize(server = 'roboRIO-3482-FRC.local')
NetworkTables.initialize(server = '10.34.82.2')
NetworkTables.enableVerboseLogging()
# NetworkTables.initialize(server = '169.254.21.97')
vision = NetworkTables.getTable("Vision")
#print(socket.gethostbyname(socket.gethostname())
#ipaddress = vision.getEntry("IP")
#ipaddress.setString(socket.gethostbyname(socket.gethostname())
centerX = vision.getEntry("centerX")
#centerY = vision.getEntry("centerY")
visionCam = vision.getEntry("visionCam")
visionCam.setDouble(0.0)
widthDev = vision.getEntry("width")
heightDev = vision.getEntry("height")
width2Dev = vision.getEntry("width2")
height2Dev = vision.getEntry("height2")
pipelines = vision.getEntry("pipeline")
pipelines.setDouble(1.0)
threshNet = vision.getEntry("thresh")
threshNet.setBoolean(False)
facingLeft = vision.getEntry
# H_LOW = vision.getEntry("H_LOW")
# H_LOW.setDouble(50)
# S_LOW = vision.getEntry("S_LOW")
# S_LOW.setDouble(70)
# L_LOW = vision.getEntry("L_LOW")
# L_LOW.setDouble(50)
# H_HIGH = vision.getEntry("H_HIGH")
# H_HIGH.setDouble(70)
# S_HIGH = vision.getEntry("S_HIGH")
# S_HIGH.setDouble(255)
# L_HIGH = vision.getEntry("L_HIGH")
# L_HIGH.setDouble(255)
targetPresent = vision.getEntry("targetPresent")
isLeftDev = vision.getEntry("isLeft")
angleDev = vision.getEntry("angle")
ticker = vision.getEntry("ticker")
ticker.setDouble(0.0)
counter = vision.getEntry("targetSelected")
distX = vision.getEntry("distX")
def partition(lst, low, high):
    i = low - 1
    pivot = lst[high]
    for j in range(low, high):
        if cv2.contourArea(lst[j]) <= cv2.contourArea(pivot):
            i += 1
            lst[i], lst[j] = lst[j], lst[i]
    lst[i + 1], lst[high] = lst[high], lst[i + 1]
    return i + 1

def quick_sort(lst, low, high):
    if low < high:
        pi = partition(lst, low, high)
        quick_sort(lst, low, pi - 1)
        quick_sort(lst, pi + 1, high)

def sort(list):
    quick_sort(list, 0, len(list) - 1)
    return list

CONTOUR_MIN_AREA = 35 #200
MIN_ASPECT_RATIO = 0.1 #0.1
MAX_ASPECT_RATIO = 10 #1
BOX_RADIUS = 10 #5
IMAGE_WIDTH = 640 #320
IMAGE_HEIGHT = 480 #240

def contourfilter(contours, img):
    # This filters out noise based off of aspect ratio and area
    gudContours = []
    for contour in contours:
        # This checks the area of the contours to see if it should be drawn or not
        if cv2.contourArea(contour) > CONTOUR_MIN_AREA:
            x, y, width, height = cv2.boundingRect(contour)
            aspectRatio = float(width) / height

            # Checks the aspect ratio to see if it fits within the required min and max
            if MIN_ASPECT_RATIO < aspectRatio < MAX_ASPECT_RATIO:
                gudContours.append(contour)
                # rect = cv2.minAreaRect(contour)
                # box = cv2.boxPoints(rect) # cv2.boxPoints(rect) for OpenCV 3.x
                # box = np.int0(box)
                # draw = cv2.drawContours(img,[box],0,(0,0,255),2)
                # toDraw = cv2.drawContours(draw, gudContours, -1, (0, 0, 255), 3)
                # cv2.rectangle(toDraw, (x, y), (x + width, y + height), (0, 255, 0),2)
                # (x,y),radius = cv2.minEnclosingCircle(contour)
                # center = (int(x),int(y))
                # radius = int(radius)
                # cv2.circle(img,center,radius,(0,255,0),2)
    return gudContours

def getcentervalues(contours):
    # grab center average of the contour list.
    # for loop to append all center values to x and y lists
    # grab average value of the lists.
    i = 0
    centerXavg = 0
    centerYavg = 0
    if len(contours) > 0:
        while (i < len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            centerX = x + int(w / 2)
            centerY = y + int(h / 2)
            centerXavg += centerX
            centerYavg += centerY
            i += 1
        centerXavg /= len(contours)
        centerYavg /= len(contours)
    return (centerXavg, centerYavg)

def getEllipseRotation(image, cnt):
    try:
        # Gets rotated bounding ellipse of contour
        ellipse = cv2.fitEllipse(cnt)
        centerE = ellipse[0]
        # Gets rotation of ellipse; same as rotation of contour
        rotation = ellipse[2]
        # Gets width and height of rotated ellipse
        widthE = ellipse[1][0]
        heightE = ellipse[1][1]
        # Maps rotation to (-90 to 90). Makes it easier to tell direction of slant
        rotation = translateRotation(rotation, widthE, heightE)

        # cv2.ellipse(image, ellipse, (23, 184, 80), 3)
        return rotation
    except:
        # Gets rotated bounding rectangle of contour
        rect = cv2.minAreaRect(cnt)
        # Creates box around that rectangle
        box = cv2.boxPoints(rect)
        # Not exactly sure
        box = np.int0(box)
        # Gets center of rotated rectangle
        center = rect[0]
        # Gets rotation of rectangle; same as rotation of contour
        rotation = rect[2]
        # Gets width and height of rotated rectangle
        width = rect[1][0]
        height = rect[1][1]
        # Maps rotation to (-90 to 90). Makes it easier to tell direction of slant
        rotation = translateRotation(rotation, width, height)
        return rotation

def translateRotation(rotation, width, height):
    if (width < height):
        rotation = -1 * (rotation - 90)
    if (rotation > 90):
        rotation = -1 * (rotation - 180)
    rotation *= -1
    return round(rotation)

def findDimensions(img, cntr):
    # colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255)]
    rect = cv2.minAreaRect(cntr)
    box = cv2.boxPoints(rect)  # cv2.boxPoints(rect) for OpenCV 3.x
    box = np.int0(box)
    area = cv2.contourArea(cntr)
    # for i in range(0, 3):
    #     cv2.circle(img, (box[i][0], box[i][1]), 10, (colors[i]), 3)
    # draw = cv2.drawContours(img, [box], 0, (0, 0, 255), 2)
    #print(box)

    point1 = box[0]
    point2 = box[1]
    point3 = box[2]
    #print(point1, point2, point3)
    distance1 = math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    distance2 = math.sqrt((point3[0] - point2[0])**2 + (point3[1] - point2[1])**2)
    width = min(distance1, distance2)
    height = max(distance1, distance2)
    #print(int(width), int(height))
    #print(height)
    return (int(width + 0.5), int(height + 0.5), int(point1[0]), int(point1[1]), int(point3[0]), int(point3[1]), area, box)

def findPairs(img, contours):
    contourArray = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        contourArray.append([contour, x, y, w, h])
    contourArray = sorted(contourArray, key=lambda x: x[1])
    pairs = []
    for i in range(len(contours) - 1):
        cntr1 = contourArray[i][0]
        cntr2 = contourArray[i + 1][0]
        angle1 = getEllipseRotation(img, cntr1)
        angle2 = getEllipseRotation(img, cntr2)
        if(np.sign(angle1) != np.sign(angle2) and angle1 < 0):
            x1, y1 = getcentervalues(cntr1)
            x2, y2 = getcentervalues(cntr2)
            xdist = distanceToX(cntr1, cntr2)
            ydist = distanceToY(cntr1, cntr2)
            w1,h1,p1x1,p1y1,p2x1,p2y1, a1, b1 = findDimensions(img, cntr1)
            w2,h2,p1x2,p1y2,p2x2,p2y2, a2, b2 = findDimensions(img, cntr2)
            # print(w1,h1, w2, h2)
            xavg = int((x1 + x2) / 2)
            yavg = int((y1 + y2) / 2)
            # x, y, z = get3DCoordinates(b1, b2, yavg)
            # print("x %d" % x)
            # print("y %d" % y)
            # print("z %d" % z)
            xtarget1 = contourArray[i][1]
            ytarget12 = contourArray[i + 1][2]
            ytarget11 = contourArray[i][2]
            ytarget1 = min(ytarget11, ytarget12)
            xtarget2 = contourArray[i + 1][1] + contourArray[i + 1][3]
            ytarget21 = contourArray[i + 1][2] + contourArray[i + 1][4]
            ytarget22 = contourArray[i][2] + contourArray[i][4]
            ytarget2 = max(ytarget21, ytarget22)
            width = xtarget2 - xtarget1
            height = max(ytarget2, ytarget21) - ytarget1
            ratio = (float(width))/height
            if((abs(p1y2 - p1y1) + abs(p2y2-p2y1)) > 6):
                cv2.rectangle(img, (xtarget1, ytarget1), (xtarget2, max(ytarget2, ytarget21)), (0, 0, 255), 2)
            else:
                cv2.rectangle(img, (xtarget1, ytarget1), (xtarget2, max(ytarget2, ytarget21)), (0, 255, 0), 2)
            cv2.circle(img, (int(xavg), int(yavg)), 5, (0, 255, 0))
            pairs.append([cntr1, cntr2, xavg, yavg, xdist[0], ydist[0], xtarget1, ytarget1, xtarget2, ytarget2, ratio, width, height])

            # cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255), 5)
    return pairs

def get3DCoordinates(box1, box2, centerY):
    img_coords = np.concatenate((box1, box2))
    # img_coords[:, 0] -= 160
    # img_coords[:, 1] -= centerY
    # img_coords[:, 1] *= -1
    img_coords = np.float32(img_coords)
    print(img_coords)
    ret, rvec, tvec = cv2.solvePnP(irl_coords, img_coords, camera_matrix, distortion, flags = cv2.SOLVEPNP_ITERATIVE)
    x = tvec[0][0]
    y = tvec[1][0]
    z = tvec[2][0]
    return (x, y, z)

def distanceToY(one, two):
    x1, y1, w1, h1 = cv2.boundingRect(one)

    x2, y2, w2, h2 = cv2.boundingRect(two)

    centerOneX = x1 + int(w1 / 2)
    centerTwoX = x2 + int(w2 / 2)
    centerOneY = y1 + int(h1 / 2)
    centerTwoY = y2 + int(h2 / 2)



    # print ("Distance To X - ", max(centerOneY, centerTwoY) - min(centerOneY, centerTwoY))
    dist = max(centerOneY, centerTwoY) - min(centerOneY, centerTwoY)
    return (dist, centerOneX, centerTwoX, centerOneY, centerTwoY)

def distanceToX(one, two):
    x1, y1, w1, h1 = cv2.boundingRect(one)

    x2, y2, w2, h2 = cv2.boundingRect(two)

    centerOneX = x1 + int(w1 / 2)
    centerTwoX = x2 + int(w2 / 2)
    centerOneY = y1 + int(h1 / 2)
    centerTwoY = y2 + int(h2 / 2)

    # print ("Distance To X - ", max(centerOneX, centerTwoX) - min(centerOneX, centerTwoX))
    dist = max(centerOneX, centerTwoX) - min(centerOneX, centerTwoX)
    return (dist, centerOneX, centerTwoX, centerOneY, centerTwoY)

def grabFeed():
    if (visionCam.getDouble(0.0) == 0.0):
        ret, capture = cam.read()
    else:
        ret, capture = cam2.read()
    # ret, capture = cam.read()
    return capture
def filter(img, H_LOW, S_LOW, L_LOW, H_HIGH, S_HIGH, L_HIGH):
    hsl = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    # 70, 90, 70
    thresh = cv2.inRange(hsl, (H_LOW, L_LOW, S_LOW), (H_HIGH, L_HIGH, S_HIGH))
    return thresh

def displayImage(img):
    cv2.imshow("Team3482 OpenCV", img)
    camera.putFrame(img)

def pipeline1():
    NetworkTables.flush()
    initial = cv2.getTickCount()
    capture = grabFeed()
    thresh = filter(capture, 50, 70, 70, 70, 255, 255)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    gudContours = contourfilter(contours, capture)

    pairs = findPairs(capture, gudContours)

    i = int(counter.getDouble(0.0))
    try:
        xavg = pairs[i][2]
        xdist = pairs[i][4]
        ratio = pairs[i][10]
        width = pairs[i][11]
        height = pairs[i][12]
        legitheight = float(502 * 5.75) / height
        if (ratio > 1):
            angle = math.degrees(math.acos(1/ratio))
            isLeft = True
        else:
            angle = math.degrees(math.acos(ratio))
            isLeft = False
    except:
        if(len(pairs) > 0):
            i = len(pairs) - 1
        else:
            i = 0
        xavg = 0
        xdist = -1
        width = 0
        height = 0
        angle = 0
        ratio = 0
        xcoord = 0
        ycoord = 0
        zcoord = 0
        legitheight = 0
        isLeft = False
    if(len(pairs) > 0):
        # widthDev.setDouble(height1)
        # heightDev.setDouble(wide1)
        # width2Dev.setDouble(height2)
        # height2Dev.setDouble(wide2)
        # print(wide1 - wide2)
        # print(height1 - height2)
        distX.setDouble(xdist)
        angleDev.setDouble(angle)
        centerX.setDouble(xavg)
        isLeftDev.setBoolean(isLeft)
        targetPresent.setBoolean(True)
    else:
        # widthDev.setDouble(0)
        # heightDev.setDouble(0)
        angleDev.setDouble(0.0)
        distX.setDouble(-1)
        centerX.setDouble(0)
        targetPresent.setBoolean(False)
    #print("ratio % d" % ratio)
    counter.setDouble(i)
    contoursNew = cv2.drawContours(capture, gudContours, -1, (240, 0, 0), 3)
    # cv2.circle(contoursNew, (int(xavg), int(yavg)), 5, (0, 255, 0))
    cv2.line(contoursNew, (int(xavg), 0), (int(xavg), 480), (255, 0, 0), 3)
    cv2.line(contoursNew, (320, 0), (320, 480), (0, 0, 255), 3)
    if(threshNet.getBoolean(False)):
        finalFrame = thresh
    else:
        finalFrame = contoursNew
    #cv2.imshow("Team3482CV", finalFrame)
    #camera.putFrame(finalFrame)
    displayImage(finalFrame)
    return(ratio, legitheight, angle)

def pipeline2():
    # x1 = 0
    # x2 = 0
    # y1 = 0
    # y2 = 0
    NetworkTables.flush()
    initial = cv2.getTickCount()
    capture = grabFeed()
    thresh = filter(capture, 50, 70, 70, 70, 255, 255)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    gudContours = contourfilter(contours, capture)

    pairs = findPairs(capture, gudContours)
    print(pairs)
    i = int(counter.getDouble(0.0))
    try:
        xavg = pairs[i][2]
        yavg = pairs[i][3]
        xdist = pairs[i][4]
        xcoord = pairs[i][15]
        ycoord = pairs[i][16]
        zcoord = pairs[i][17]
    except:
        if (len(pairs) > 0):
            i = len(pairs) - 1
        else:
            i = 0
        print("lamo you tard")
        xavg = 0
        yavg = 0
        xdist = -1
        xcoord = 0
        ycoord = 0
        zcoord = 0
    if(len(pairs) > 0):
        distX.setDouble(xdist)
        centerX.setDouble(xavg)
        #centerY.setDouble(yavg)
        targetPresent.setBoolean(True)
    else:
        distX.setDouble(-1)
        centerX.setDouble(0)
        #centerY.setDouble(0)
        targetPresent.setBoolean(False)
    distX.setDouble(xdist)
    counter.setDouble(i)
    fps = cam.get(cv2.CAP_PROP_FPS)
    # print(fps)
    contoursNew = cv2.drawContours(capture, gudContours, -1, (240, 0, 0), 3)
    # cv2.circle(contoursNew, (int(xavg), int(yavg)), 5, (0, 255, 0))
    cv2.line(contoursNew, (int(xavg), 0), (int(xavg), IMAGE_HEIGHT), (255, 0, 0), 3)
    cv2.line(contoursNew, (int(IMAGE_WIDTH/2), 0), (int(IMAGE_WIDTH/2), IMAGE_HEIGHT), (0, 0, 255), 3)
    displayImage(contoursNew)
    final = cv2.getTickCount()
    #fps = float((final - initial))/cv2.getTickFrequency()
    #print("FPS: %d" % fps)
    print(xcoord, ycoord, zcoord)
    return (xcoord, ycoord, zcoord)


def pipeline3():
    capture = grabFeed()
    displayImage(capture)

def redo():
    j = 0
    while(True):
        pipe = 1
        #print("print % d" % pipe)
        if(pipe == 1):
            x, y, z = pipeline1()
            if (j % 15 == 0):
                print(x, y, z)
            j += 1
        elif(pipe == 2):
            pipeline2()
        elif(pipe == 3):
            pipeline3()
        else:
            pipe = 1
        if (ticker.getDouble(0.0) == 0.0):
            ticker.setDouble(1.0)
        else:
            ticker.setDouble(0.0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break



redo()
cam.release()
cv2.destroyAllWindows()
