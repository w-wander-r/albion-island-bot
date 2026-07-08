import cv2 as cv
import numpy as np
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def findClickPositions(needle_image_path, haystack_image_path, threshold=0.55, debug_mode=None):
    haystack_img = cv.imread('farm.png', cv.IMREAD_UNCHANGED)
    needle_image = cv.imread('cabbage.png', cv.IMREAD_UNCHANGED)
    needle_w = needle_image.shape[1]
    needle_h = needle_image.shape[0]

    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack_img, needle_image, method)

    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
        rectangles.append(rect)
        rectangles.append(rect)

    rectangles, weight = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
    
    points = []
    if len(rectangles):
        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        for (x, y, w, h) in rectangles:

            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))

            if debug_mode == 'rectangles':
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                cv.rectangle(haystack_img, top_left, bottom_right, color=line_color, 
                             lineType=line_type, thickness=2)
            elif debug_mode == 'points':
                cv.drawMarker(haystack_img, (center_x, center_y), 
                              color=marker_color, markerType=marker_type, 
                              markerSize=40, thickness=2)

        if debug_mode:
            cv.imshow('Matches', haystack_img)
            cv.waitKey()
            cv.destroyAllWindows()

    return points

points = findClickPositions('cabbage.jpg', 'farm.jpg', debug_mode='points')
print(points)

points = findClickPositions('cabbage.jpg', 'farm.jpg', 
                            threshold=0.70, debug_mode='rectangles')
print(points)