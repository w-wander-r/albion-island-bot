import cv2 as cv
import numpy as np
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

haystack_image = cv.imread('farm.png', cv.IMREAD_UNCHANGED)
needle_image = cv.imread('cabbage.png', cv.IMREAD_UNCHANGED)

needle_w = needle_image.shape[1]
needle_h = needle_image.shape[0]

result = cv.matchTemplate(haystack_image, needle_image, cv.TM_CCOEFF_NORMED)

min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

threshold = 0.55
locations = np.where(result >= threshold)
locations = list(zip(*locations[::-1]))

rectangles = []
for loc in locations:
    rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
    rectangles.append(rect)
    rectangles.append(rect)

rectangles, weight = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

if len(rectangles):

    line_color = (0, 255, 0)  # Green color in BGR
    line_type = cv.LINE_4
    marker_color = (0, 0, 255)  # Red color in BGR
    marker_type = cv.MARKER_CROSS
    
    for (x, y, w, h) in rectangles:
        # top_left = (x, y)
        # bottom_right = (x + w, y + h)
        # cv.rectangle(haystack_image, top_left, bottom_right, line_color, lineType=line_type)
        center_x = x + int(w / 2)
        center_y = y + int(h / 2)
        cv.drawMarker(haystack_image, (center_x, center_y), 
                      marker_color, markerType=marker_type, markerSize=40, thickness=2)


    cv.imshow('Detected', haystack_image)
    cv.waitKey()
    cv.destroyAllWindows()
else:
    print("No match found.")