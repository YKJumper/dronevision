import cv2
import datetime;
ct = datetime.datetime.now()
print("current time:-", ct)
 
img = cv2.imread('city.jpg', cv2.IMREAD_UNCHANGED)
 
print('Original Dimensions : ',img.shape)

# persents = [95]
scale_percent = 47 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)

for i in range(1000):
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

ct = datetime.datetime.now()
print("current time:-", ct)

print('Resized Dimensions : ',resized.shape)
 
cv2.imshow("Resized image", resized)
cv2.waitKey(0)
cv2.destroyAllWindows()