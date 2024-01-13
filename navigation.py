import numpy as np
import math
import cv2 as cv
from matplotlib import pyplot as plt

__REatrh__ = 6367486

def sqrEquation(A, B, C):
    D = B**2 - 4*A*C
    if D < 0:
        return (0, -1, -1)
    elif D == 0:
        x1 = -B / (2*A)
        return (1, x1, x1)
    else:
        x1 = (-B + math.sqrt(D)) / (2*A)
        x2 = (-B - math.sqrt(D)) / (2*A)
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


def distanceApprox(A, B, C, mAB, mBC, mCA):
    eps = 0.001
    lmin = 0
    lmax = min(mCA/math.tan(C/180*math.pi), mAB/math.tan(A/180*math.pi))
    l1 = (lmin + lmax)/2
    # Finding l3
    l3y = l1 * math.sin(C/180*math.pi)
    l3x = l1 * math.cos(C/180*math.pi)
    l3 = l3x + (mCA**2 - l3y**2)**0.5

    # Finding l2
    l2y = l1 * math.sin(A/180*math.pi)
    l2x = l1 * math.cos(A/180*math.pi)
    l2 = l2x + (mAB**2 - l2y**2)**0.5

    # Finding mBC`
    mBC0 =(l2**2 + l3**2 - 2*l2*l3*math.cos(B/180*math.pi))**0.5
    while math.fabs(mBC-mBC0)/mBC0 > eps:
        if mBC-mBC0 < 0:
            lmax = l1
            l1 = (l1 + lmin)/2
        else:
            lmin = l1
            l1 = (l1 + lmax)/2
            
        # Finding l3
        l3y = l1 * math.sin(C/180*math.pi)
        l3x = l1 * math.cos(C/180*math.pi)
        l3 = l3x + (mCA**2 - l3y**2)**0.5

        # Finding l2
        l2y = l1 * math.sin(A/180*math.pi)
        l2x = l1 * math.cos(A/180*math.pi)
        l2 = l2x + (mAB**2 - l2y**2)**0.5

        # Finding mBC`
        mBC0 =(l2**2 + l3**2 - 2*l2*l3*math.cos(B/180*math.pi))**0.5
    return (l1, l2, l3)

def triangPosition(A, B, C, Ap, Bp, Cp, pHight, pWidth, focus35):
    # A, B, C    -- Physical coordinates of templates. A located before B, B before C. A[0] is Latitude decimals, A[1] - longitude, A[2] - elevation
    # Ap, Bp, Cp -- Coordinates of templates in pixels (left upper corner has (0,0) coordinats). Ap[0] is Y coordinate (vertical), Ap[1] is X coordinate (horizontal)
    # focus35    -- Focal length in 35mm equiv. Depends on a camera model and resolution
    # pWidth     -- Horizontal image size in pixels. Depends on a camera model and resolution

    # Convert coordinates
    Am = Convert2Meters(A)
    Bm = Convert2Meters(B)
    Cm = Convert2Meters(C)

    # Find vectors in base of  trianle ABC
    CAm = addVectors(Am, mltVectorReal(Cm, -1))
    CBm = addVectors(Bm, mltVectorReal(Cm, -1))

    # Find distances between opjects
    mAB = dist(Am, Bm)
    mBC = dist(Bm, Cm)
    mCA = dist(Cm, Am)

    # Find opjects' coordinates on the camera matrix
    Amm = Convert2mm(Ap, pWidth)
    Bmm = Convert2mm(Bp, pWidth)
    Cmm = Convert2mm(Cp, pWidth)
    # Define the lenses focus coordinates in mm on the camera matrix
    Op = (pHight//2, pWidth//2)
    Omm = Convert2mm(Op, pWidth); Omm[2] = Omm[2]+focus35

    # Find angles between opjects
    aAB = realAng(Omm, Amm, Bmm)
    aBC = realAng(Omm, Bmm, Cmm)
    aCA = realAng(Omm, Amm, Cmm)

    # Finding real disatnses between a view point (pooint O) and visible objects A, B, C
    Dst = distanceApprox(aAB, aBC, aCA, mAB, mBC, mCA)
    l1 = Dst[0]; l2 = Dst[1]; l3 = Dst[2]


    sin_phi = l1/mCA*math.sin(aCA/180*math.pi); cos_phi = (1 - sin_phi**2)**0.5; mCM = l3*cos_phi
    sin_etha = l2/mBC*math.sin(aBC/180*math.pi); cos_etha = (1 - sin_etha**2)**0.5; mCN = l3*cos_etha

    CAm0 = normVector(CAm)
    CBm0 = normVector(CBm)

    CMm = mltVectorReal(CAm0, mCM)
    CNm = mltVectorReal(CBm0, mCN)

    Mm = addVectors(Cm, CMm)
    Nm = addVectors(Cm, CNm)

    nABC = mltVectors(CBm, CAm)
    nABC0 = normVector(nABC)

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

# # proxima2/Z1 
# pWidth = 4896
# pHight = 3672
# focus35 = 20

# Ap = (2289, 3591)
# Bp = (1832, 2126)
# Cp = (1805, 2600)

A = (49.881378, 24.032703, 289)
B = (49.877974, 24.030494, 322)
C = (49.877675, 24.027882, 331)
# O = (49.882253, 24.035912, 318)

pWidth = 1920
pHight = 1080
focus35 = 35*(1150-307)/1413

Ap = (704, 604)
Bp = (315, 430)
Cp = (196, 576)

print(triangPosition(A, B, C, Ap, Bp, Cp, pHight, pWidth, focus35))