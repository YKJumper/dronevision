
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

def dist(a, b):
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def lst2Str(s):
     str1 = ""
     for n in s:
        str1 += str(n) + ","
     return str1


# All the 6 methods for comparison in a list
# methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR', 'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
methods = ['cv.TM_CCOEFF_NORMED']
# rectangle color in BGR 
color = (0, 0, 255) 
# Line thickness of 2 px 
thickness = 2
# images = ['', '', '', '', '', '', '', '','', '']
template = cv.imread('proxima/target-t.jpg', cv.IMREAD_GRAYSCALE)
template_ver = cv.imread('proxima/target-v.jpg', cv.IMREAD_GRAYSCALE)
assert template is not None, "file could not be read, check with os.path.exists()"
w = template.shape[1]
h = template.shape[0]

# Show target template
print('Template dimensions : ',template.shape)
cv.imshow("Template image:", template)
cv.waitKey(0)

print('Template verification dimensions : ',template_ver.shape)
cv.imshow("Template verification image ", template_ver)
cv.waitKey(0)

images_zoom = [1,105/20,157/20,223/20,319/20,20,469/20,515/20,681/20,778/20,947/20,50,1132/20,60]
images_name = [1,5,8,11,16,20,24,26,34,39,47,50,57,60]
images_cnt = len(images_zoom)
for j in range(images_cnt):
    image_name = 'proxima/Z'+str(images_name[j])+'.jpg'
    img = cv.imread(image_name, cv.IMREAD_GRAYSCALE)
    assert img is not None, "file could not be read, check with os.path.exists()"

    scale_times = images_zoom[j] * 1.05
    width = int(img.shape[1] / scale_times)
    height = int(img.shape[0] / scale_times)
    dim = (width, height)

    resized = cv.resize(img, dim, interpolation = cv.INTER_LINEAR)
    # print('Resized Dimensions : ',resized.shape)
    # cv.imshow("Resized image "+image_name, resized)
    # cv.waitKey(0)
    img = resized.copy()

    for meth in methods:
        method = eval(meth)
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
        dst = dist(top_left_ver, top_left)
        if dst <= h/3:
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv.rectangle(img, top_left, bottom_right, color, thickness)
            plt.subplot(121), plt.imshow(res, cmap='gray')
            plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
            plt.subplot(122), plt.imshow(img, cmap='gray')
            plt.title('Detected Point at '+image_name), plt.xticks([]), plt.yticks([])
            plt.suptitle(meth)
            plt.show()
            cv.waitKey(0)
        else:
            print('by method:', meth, ' -- template was not found in image ', image_name)
