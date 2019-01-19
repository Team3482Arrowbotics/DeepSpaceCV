#!/usr/bin/env python3

# Grabs the average coordinates for the contour and then prints them
# todo: add networktables and sorting for filtering

import cv2

# from networktables import NetworkTables

cam = cv2.VideoCapture(0)

x = 0
y = 0
w = 0
h = 0
area = 0
xavg = 0


# NetworkTables.initialize(server = 'roboRIO-3482-frc.local')
# vision = NetworkTables.getTable("Vision")
# centerX = vision.getEntry("centerX")
# centerY = vision.getEntry("centerY")

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


CONTOUR_MIN_AREA = 750
MIN_ASPECT_RATIO = 0.5
MAX_ASPECT_RATIO = 2
BOX_RADIUS = 10
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

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
                toDraw = cv2.drawContours(img, gudContours, -1, (0, 0, 255), 3)
                cv2.rectangle(toDraw, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return gudContours

def getcentervalues(contours):
    # grab center average of the contour list.
    # for loop to append all center values to x and y lists
    # grab average value of the lists.
    i = 0
    centerXavg = 0
    centerYavg = 0
    if len(contours) > 0:
        while(i < len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            centerX = x + int(w / 2)
            centerY = y + int(h / 2)
            centerXavg += centerX
            centerYavg += centerY
            i += 1
        centerXavg /= len(contours)
        centerYavg /= len(contours)
    return (centerXavg, centerYavg)




def redo():
    while (True):
        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0
        ret, capture = cam.read()
        hsl = cv2.cvtColor(capture, cv2.COLOR_BGR2HLS)
        thresh = cv2.inRange(hsl, (62, 71, 78), (180, 255, 255))
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        gudContours = contourfilter(contours, capture)

        xavg, yavg = getcentervalues(gudContours)

        print("xavg: %d" %xavg)
        print("yavg: %d" %yavg)

        contoursNew = cv2.drawContours(capture, gudContours, -1, (240, 0, 0), 3)
        cv2.circle(contoursNew, (xavg, yavg), 5, (0, 255, 0))
        cv2.imshow("Team3482 OpenCV", contoursNew)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        inRange = None

        # # This is drawing the boxes around contours
        # contoursNew = capture
        # if len(gudContours) > 0:
        #     contoursNew = cv2.drawContours(capture, gudContours, -1, (240, 0, 0), 3)
        #     counter = 0
        #     for contour in contoursNew:
        #         x, y, width, height = cv2.boundingRect(contour)
        #         if counter % 2 == 0:
        #             x1 = x
        #             y1 = y
        #         else:
        #             x2 = x
        #             y2 = y
        #         counter += 1
        #
        #         centerX = x + int(width / 2)
        #         centerY = y + int(height / 2)
        #
        #         cv2.rectangle(contoursNew, (x, y), (x + width, y + height), (0, 255, 0), 2)
        #         cv2.circle(contoursNew, (centerX, centerY), BOX_RADIUS, (255, 0, 0), -1)
        #
        #         rangeX = abs(centerX - IMAGE_WIDTH / 2)
        #         rangeY = abs(centerY - IMAGE_HEIGHT / 2)
        #
        #         #
        #         xavg = (x1 + x2)/2
        #
        #         inRange = rangeX <= (IMAGE_WIDTH / 8) and rangeY <= (IMAGE_HEIGHT / 8)
        #
        #         cv2.line(contoursNew, (xavg, 0), (xavg, 480), (255, 0, 0), 5)
        #         cv2.line(contoursNew, (320, 0), (320, 480), (0, 0, 255), 1)
        #
        #         if inRange:
        #             cv2.rectangle(contoursNew, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #             cv2.circle(contoursNew, (centerX, centerY), 10, (0, 0, 255), 1)
        #
        #         else:
        #             cv2.rectangle(contoursNew, (240, 180), (400, 300), (0, 255, 0), 2)
        #             cv2.circle(contoursNew, (320, 240), 5, (0, 255, 0), -1)
        #
        # # print(x, " - ", y)
        # print("In Range - ", inRange)
        # print("Center - ", xavg)
        # print(len(contours))

        # contoursNew = cv2.drawContours(capture, gudContours, -1, (240, 0, 0), 3)
        # cv2.imshow("Team3482 OpenCV", contoursNew)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

redo()
cam.release()
cv2.destroyAllWindows()
# while (True):
#     ret, capture = cam.read()
#     hsl = cv2.cvtColor(capture, cv2.COLOR_BGR2HLS)
#     thresh = cv2.inRange(hsl, (62, 71, 78), (180, 255, 255))
#     im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     gudcntrs = []
#     cntrss = False
#     # cntr = sort(contours)
#     for cntr in contours:
#         if (cv2.contourArea(cntr) > 375):
#             x, y, w, h = cv2.boundingRect(cntr)
#             area = cv2.contourArea(cntr)
#             aspect_ratio = float(w) / h
#             if (0.5 < aspect_ratio < 2):
#                 gudcntrs.append(cntr)
#                 cntrss = True
#                 cntrs = cv2.drawContours(capture, gudcntrs, -1, (0, 0, 255), 3)
#                 cv2.rectangle(cntrs, (x, y), (x + w, y + h), (0, 255, 0), 2)
#             else:
#                 cntrss = False
#     inRange = None
#     if (cntrss == True):
#         x1 = 0
#         x2 = 0
#         y1 = 0
#         y2 = 0
#         counter = 0
#         cntrs = cv2.drawContours(capture, gudcntrs, -1, (240, 0, 0), 3)
#         for cntr in gudcntrs:
#             one, two, three, four = cv2.boundingRect(cntr)
#             a = one + int(three / 2)
#             b = two + int(four / 2)
#             cv2.rectangle(cntrs, (one, two), (one + three, two + four), (0, 255, 0), 2)
#             cv2.circle(cntrs, (a, b), 10, (255, 0, 0), -1)
#             c = abs(a - 320)
#             d = abs(b - 240)
#         if (c <= 80 and d <= 60):
#             inRange = True
#         else:
#             inRange = False
#         a = x + int(w / 2)
#         b = y + int(h / 2)
#         if (counter % 2 == 0):
#             x1 = a
#             y1 = a
#         elif (counter % 2 == 1):
#             x2 = a
#             y2 = a
#         counter += 1
#         xavg = (x1 + x2) / 2
#         cv2.rectangle(cntrs, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         cv2.circle(cntrs, (a, b), 10, (0, 0, 255), -1)
#         cv2.line(cntrs, (xavg, 0), (xavg, 480), (255, 0, 0), 5)
#         cv2.line(cntrs, (320, 0), (320, 480), (0, 0, 255), 1)
#     else:
#         cntrs = capture
#     if (inRange):
#         cv2.rectangle(cntrs, (240, 180), (400, 300), (0, 255, 0), 2)
#         cv2.circle(cntrs, (320, 240), 5, (0, 255, 0), -1)
#     else:
#         cv2.rectangle(cntrs, (240, 180), (400, 300), (0, 0, 255), 2)
#         cv2.circle(cntrs, (320, 240), 5, (0, 0, 255), -1)
#     cv2.imshow("Team3482 OpenCV", cntrs)
#     # centerX.setDouble(x)
#     # centerY.setDouble(y)
#     print(x, " - ", y)
#     print("In Range - ", inRange)
#     print("Area - ", area)
#     print("Center - ", xavg)
#     print(len(contours))
#     # print(centerX.getDouble(0.0))
#     # print(centerY.getDouble(0.0))
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# # When everything done, release the capture
# cam.release()
# cv2.destroyAllWindows()
