import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
images = ['./foto/Z1.JPG', './foto/Z5.JPG', './foto/Z8.JPG', './foto/Z11.JPG', './foto/Z16.JPG', './foto/Z20.JPG', './foto/Z24.JPG', './foto/Z26.JPG', './foto/Z34.JPG', './foto/Z39.JPG', './foto/Z47.JPG', './foto/Z50.JPG', './foto/Z57.JPG', './foto/Z60.JPG']
template = cv.imread('./foto/Z-0-50R0.jpg', cv.IMREAD_GRAYSCALE)
template_ver = cv.imread('./foto/Z-1-50R0.jpg', cv.IMREAD_GRAYSCALE)
color = (0, 0, 255)
assert template is not None, "file could not be read, check with os.path.exists()"
w, h = template.shape[::-1]
# All the 6 methods for comparison in a list
# methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR', 'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
method2use = 'cv.TM_CCOEFF_NORMED'
for frame in images:
    img = cv.imread(frame, cv.IMREAD_GRAYSCALE)
    assert img is not None, "file could not be read, check with os.path.exists()"
    # img2 = img.copy()
    # img = img2.copy()
    method = eval(method2use)
    # Apply template Matching
    res = cv.matchTemplate(img, template, method)
    res_ver = cv.matchTemplate(img, template_ver, method)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    min_val_ver, max_val_ver, min_loc_ver, max_loc_ver = cv.minMaxLoc(res_ver)
    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
        top_left = min_loc
        top_left_ver = min_loc_ver
    else:
        top_left = max_loc
        top_left_ver = max_loc_ver
    if top_left_ver == top_left:
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv.rectangle(img, top_left, bottom_right, 255, 2)
        plt.subplot(121), plt.imshow(res, cmap='gray')
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(img, cmap='gray')
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.suptitle(method2use)
        plt.show()
    else:
        print('method:', method2use, ' frame:', frame, ' -- template was not found.')

