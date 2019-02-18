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
        wide1 = pairs[i][11]
        wide2 = pairs[i][12]
        height1 = pairs[i][13]
        height2 = pairs[i][14]
    except:
        if(len(pairs) > 0):
            i = len(pairs) - 1
        else:
            i = 0
        xavg = 0
        xdist = -1
        wide1 = 0
        wide2 = 0
        height1 = 0
        height2 = 0
    #print("ratio % d" % ratio)
    contoursNew = cv2.drawContours(capture, gudContours, -1, (240, 0, 0), 3)
    # cv2.circle(contoursNew, (int(xavg), int(yavg)), 5, (0, 255, 0))
    cv2.line(contoursNew, (int(xavg), 0), (int(xavg), 480), (255, 0, 0), 3)
    cv2.line(contoursNew, (320, 0), (320, 480), (0, 0, 255), 3)
    if(threshNet.getBoolean(False)):
        finalFrame = thresh
    else:
        finalFrame = contoursNew
    #cv2.imshow("Team3482CV", finalFrame)
while(True):
    pipeline1()