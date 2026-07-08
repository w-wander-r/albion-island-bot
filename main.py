import cv2 as cv
import numpy as np

haystack_image = cv.imread('farm.png', cv.IMREAD_UNCHANGED)
needle_image = cv.imread('cabbage.png', cv.IMREAD_UNCHANGED)

result = cv.matchTemplate(haystack_image, needle_image, cv.TM_CCOEFF_NORMED)

min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

threshold = 0.55
locations = np.where(result >= threshold)
locations = list(zip(*locations[::-1]))

if locations:
    print(f"Match found at location: {max_loc} with value: {max_val}")

    needle_w = needle_image.shape[1]
    needle_h = needle_image.shape[0]
    line_color = (0, 255, 0)  # Green color in BGR
    line_type = cv.LINE_4
    
    for loc in locations:
        top_left = loc
        bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
        cv.rectangle(haystack_image, top_left, bottom_right, line_color, lineType=line_type)

    cv.imshow('Detected', haystack_image)
    cv.waitKey()
else:
    print("No match found.")

print(f"Max value: {max_val}, Max location: {max_loc}")
print(f"Min value: {min_val}, Min location: {min_loc}")