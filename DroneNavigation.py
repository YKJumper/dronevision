import numpy as np
import math
import cv2 as cv
from matplotlib import pyplot as plt
import datetime as date

__REatrh__ = 6367486

def sqrEquation(A, B, C):
    D = B**2 - 4*A*C
    if D < 0:
        return (0, -1, -1)
    elif D == 0:
        x1 = -B / (2*A)
        return (1, x1, x1)
    else:
        x1 = (-B + (D)**0.5) / (2*A)
        x2 = (-B - (D)**0.5) / (2*A)
        return (2, min(x1, x2), max(x1, x2))

# Convert ccordinates
def Convert2Meters (X):
    REarth = (6378137 + 6356752)/2
    mLatpgrad = 2*math.pi*REarth/360
    mLonpgrad = 2*math.pi*REarth*math.cos(X[0]/180*math.pi)/360
    return [(X[0]-49)*mLatpgrad, (X[1]-24)*mLonpgrad, X[2]]

def Convert2Decimals (X):
    REarth = (6378137 + 6356752)/2
    mLatpgrad = 2*math.pi*REarth/360
    X[0] = X[0]/mLatpgrad+49
    mLonpgrad = 2*math.pi*REarth*math.cos(X[0]/180*math.pi)/360
    X[1] = X[1]/mLonpgrad+24
    return X

# Convert ccordinates
def Convert2mm (Xp, widthPixels):
    pSize = 35/widthPixels
    return [Xp[0]*pSize, Xp[1]*pSize, 0]

def dist(a, b):
    n = min(len(a), len(b))
    d = 0
    for i in range(n):
        d += (a[i] - b[i])**2
    return d**0.5

def addVectors(a, b):
    n = min(len(a), len(b))
    d1 = []
    for i in range(n):
        d1.append(a[i] + b[i])
    return d1

def mltVectorReal(a, b):
    n = len(a)
    d = []
    for i in range(n):
        d.append(a[i]*b)
    return d

def mltVectors(a, b):
    n = min(len(a), len(b))
    d = []
    if n == 3:
        d.append(a[1] * b[2] - a[2] * b[1])
        d.append(a[2] * b[0] - a[0] * b[2])
        d.append(a[0] * b[1] - a[1] * b[0])
    return d

def mltVectorsScalar(a, b):
    n = min(len(a), len(b))
    d = 0
    for i in range(n):
        d += a[i] * b[i]
    return d

def absVector(a):
    return mltVectorsScalar(a, a)**0.5

def normVector(a):
    return mltVectorReal(a, 1/absVector(a))

def realAng(a, b, c):
    n = min(len(a), len(b))
    ab = dist(a, b)
    ac =  dist(a, c)
    sbc = 0
    for i in range(n):
        sbc += (b[i] - a[i])*(c[i] - a[i])
    realAng = math.acos(sbc/(ab*ac))/math.pi*180
    return realAng

def lst2Str(s):
     str1 = ""
     for n in s:
        str1 += str(n) + ","
     return str1

def matchScaledTemplate(template, img, meth, template_ver, zoom_step, min_degree):
    h = template.shape[0]; w = template.shape[1]
    Wi = img.shape[1]; Hi = img.shape[0]
    Wtv = template_ver.shape[1]; Htv = template_ver.shape[0]
    maxScale = min(int(math.log(2*Wtv/Wi, zoom_step)), int(math.log(2*Htv/Hi, zoom_step)))
    scalePers = range(min_degree, maxScale)
    for j in scalePers:
        zoomValue = zoom_step ** j
        width = int(Wi * zoomValue); height = int(Hi * zoomValue)
        dim = (width, height)

        resized = cv.resize(img, dim, interpolation = cv.INTER_LINEAR)

        method = eval(meth)
        # Apply template Matching
        res = cv.matchTemplate(resized, template, method)
        res_ver = cv.matchTemplate(resized, template_ver, method)
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
        if dst <= h:
            top_left = (int(top_left[0] / zoomValue), int(top_left[1] / zoomValue))
            bottom_right = (int((top_left[0] + w) / zoomValue), int((top_left[1] + h) / zoomValue))
            # Define the coordinates of the new template in the image
            scaleCoef = 1 / zoomValue; h_shift = 2 * h * scaleCoef; w_shift = 2 * w * scaleCoef
            vx1, vy1, vx2, vy2 = top_left[0], top_left[1], int(top_left[0] + w_shift), int(top_left[1] + h_shift)
            # Extract the templates
            template_ver = img[vy1:vy2, vx1:vx2].copy()
            # template = template_ver[int((vy2-vy1)/2):vy2-vy1, int((vx2-vx1)/2):vx2-vx1].copy()
            return top_left, bottom_right, j, template_ver
    return [-1, -1], [-1, -1], 0

def distanceApprox(A, B, C, mAB, mBC, mCA):
    mBC2 = mBC*mBC
    eps = 0.001
    lmin = 0
    # Optimization of the calculation
    angA = A/180*math.pi; angB = B/180*math.pi; angC = C/180*math.pi
    sinA = math.sin(angA); cosA =  math.cos(angA)
    cosB = math.cos(angB)
    sinC = math.sin(angC); cosC = math.cos(angC)

    lmax = min(mCA/sinC*cosC, mAB/sinA*cosA)
    l1 = (lmin + lmax)/2

    # Finding l3
    l3y = l1 * sinC; l3x = l1 * cosC; l3 = l3x + (mCA**2 - l3y**2)**0.5

    # Finding l2
    l2y = l1 * sinA; l2x = l1 * cosA; l2 = l2x + (mAB**2 - l2y**2)**0.5

    # Finding mBC`
    mBC02 =l2**2 + l3**2 - 2*l2*l3*cosB
    while math.fabs(mBC2-mBC02)/mBC2 > eps:
        if mBC2-mBC02 < 0:
            lmax = l1; l1 = (l1 + lmin)/2
        else:
            lmin = l1; l1 = (l1 + lmax)/2
            
        # Finding l3
        l3y = l1 * sinC; l3x = l1 * cosC; l3 = l3x + (mCA**2 - l3y**2)**0.5

        # Finding l2
        l2y = l1 * sinA; l2x = l1 * cosA; l2 = l2x + (mAB**2 - l2y**2)**0.5

        # Finding mBC`
        mBC02 =l2**2 + l3**2 - 2*l2*l3*cosB
    return (l1, l2, l3)

def triangPosition(A, B, C, Ap, Bp, Cp, pHight, pWidth, focus35):
    # A, B, C    -- Physical coordinates of templates. A located before B, B before C. A[0] is Latitude decimals, A[1] - longitude, A[2] - elevation
    # Ap, Bp, Cp -- Coordinates of templates in pixels (left upper corner has (0,0) coordinats). Ap[0] is Y coordinate (vertical), Ap[1] is X coordinate (horizontal)
    # focus35    -- Focal length in 35mm equiv. Depends on a camera model and resolution
    # pWidth     -- Horizontal image size in pixels. Depends on a camera model and resolution

    # Convert coordinates
    Am = Convert2Meters(A); Bm = Convert2Meters(B); Cm = Convert2Meters(C)

    # Find vectors in base of  trianle ABC
    CAm = addVectors(Am, mltVectorReal(Cm, -1)); CBm = addVectors(Bm, mltVectorReal(Cm, -1))

    # Find distances between opjects
    mAB = dist(Am, Bm); mBC = dist(Bm, Cm); mCA = dist(Cm, Am)

    # Find opjects' coordinates on the camera matrix
    Amm = Convert2mm(Ap, pWidth); Bmm = Convert2mm(Bp, pWidth); Cmm = Convert2mm(Cp, pWidth)
    # Define the lenses focus coordinates in mm on the camera matrix
    Op = (pHight//2, pWidth//2); Omm = Convert2mm(Op, pWidth); Omm[2] = Omm[2]+focus35

    # Find angles between opjects
    aAB = realAng(Omm, Amm, Bmm); aBC = realAng(Omm, Bmm, Cmm); aCA = realAng(Omm, Amm, Cmm)

    # Finding real disatnses between a view point (pooint O) and visible objects A, B, C
    Dst = distanceApprox(aAB, aBC, aCA, mAB, mBC, mCA)
    l1 = Dst[0]; l2 = Dst[1]; l3 = Dst[2]


    sin_phi = l1/mCA*math.sin(aCA/180*math.pi); cos_phi = (1 - sin_phi**2)**0.5; mCM = l3*cos_phi
    sin_etha = l2/mBC*math.sin(aBC/180*math.pi); cos_etha = (1 - sin_etha**2)**0.5; mCN = l3*cos_etha

    CAm0 = normVector(CAm); CBm0 = normVector(CBm)

    CMm = mltVectorReal(CAm0, mCM); CNm = mltVectorReal(CBm0, mCN)

    Mm = addVectors(Cm, CMm); Nm = addVectors(Cm, CNm)

    nABC = mltVectors(CBm, CAm); nABC0 = normVector(nABC)

    # nM = normVector(mltVectors(CAm0, nABC0))
    nN = normVector(mltVectors(CBm0, nABC0))

    r = mltVectorsScalar(addVectors(Mm, mltVectorReal(Nm, -1)), CAm)/mltVectorsScalar(nN, CAm)
    # p = mltVectorsScalar(addVectors(Nm, mltVectorReal(Mm, -1)), CBm)/mltVectorsScalar(nM, CBm)
    Ohm = addVectors(Nm, mltVectorReal(nN, r))
    # Oh = Convert2Decimals(Ohm)
    # Ohmp = addVectors(Mm, mltVectorReal(nM, p))
    OhCm = absVector(addVectors(Cm, mltVectorReal(Ohm, -1)))
    h = (l3**2 - OhCm**2)**0.5

    if nABC0[2] < 0:
        nABC0 = mltVectorReal(nABC0, -1)

    Om = addVectors(Ohm, mltVectorReal(nABC0, h))
    O = Convert2Decimals(Om)
    return O

### ================== View point position finding
# Find a view point position by proxima2/Z1 image
# pWidth = 4896
# pHight = 3672
# focus35 = 20

# Ap = (2289, 3591)
# Bp = (1832, 2126)
# Cp = (1805, 2600)

# A = (49.881378, 24.032703, 289)
# B = (49.877974, 24.030494, 322)
# C = (49.877675, 24.027882, 331)
# # O = (49.882253, 24.035912, 318)

# # Find a view point position by image path1/GoogleMaps-P1.jpg
# pWidth = 1920
# pHight = 1080
# focus35 = 35*(1150-307)/1413

# Ap = (704, 604)
# Bp = (315, 430)
# Cp = (196, 576)

# now = date.datetime.now()
# lp = 50000
# for i in range(lp):
#     # print(triangPosition(A, B, C, Ap, Bp, Cp, pHight, pWidth, focus35))
#      triangPosition(A, B, C, Ap, Bp, Cp, pHight, pWidth, focus35)
# print((date.datetime.now() - now)/lp*1000)

### ================== MatchTemplate
degree = 0
scaleStep = 0.9
meth = 'cv.TM_CCOEFF_NORMED'
template = cv.imread('proxima3/target-t.jpg', cv.IMREAD_GRAYSCALE)
template_ver = cv.imread('proxima3/target-v.jpg', cv.IMREAD_GRAYSCALE)
# assert template is not None, "file could not be read, check with os.path.exists()"
image_name = 'proxima3/F1.jpg'
img = cv.imread(image_name, cv.IMREAD_GRAYSCALE)
# assert img is not None, "file could not be read, check with os.path.exists()"
method = eval(meth)
now = date.datetime.now()
lp = 100
for i in range(lp):
    resPos = matchScaledTemplate(template, img, meth, template_ver, scaleStep, degree)
print((date.datetime.now() - now)/lp*1000)
print(resPos[2])