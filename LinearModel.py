import math
import datetime as date

StateHistory = [] # Sate history list
Ra = 50 # Rotation center coordinates in xOy (0,-Ra)
dt = 500 # Correction period 2*dt, ms

#region ============ External Functions
def GetTargetPosition(ObjectId):
    # Return position of tracked object in local coordinates x`O`y`
    # xl yl = TrackObject(ObjectId)
    xl = 0
    yl = 0
    return xl, yl

def GetBodyState():
    # Return body orientation Roll, Pitch, Yaw and throttle level St in [0;1]
    Phi = 0
    Theta = 0
    Psi = 0
    St = 0
    return Phi, Theta, Psi, St

def InitGuidingParameters():
    # Setinitial values of guiding paameters
    # Se (Dynamic) == the equilibrium position of throttle signal
    # Phie (Dynamic) == the equilibrium position of throttle signal
    Phi, Theta, Psi, St = GetBodyState()
    Amax = 1000
    Se = St
    Phie = Phi
    Theta0 = Theta
    Psi0 =  Psi
    GuideParams = {"deltatime": dt, "amax": Amax, "Phie": Phie, "Theta0": Theta0, "Psi0": Psi0, "Se": Se}
    return GuideParams
#endregion

#region ============ Auxilary Functions
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

def GradToRad(degrees):
    radians = degrees/180*math.pi
    return radians
#endregion ===============================

#region ============ Guiding Functions
def ScreenTransformationXY(xl, yl, Phi):
    # x`O`y` -- відносна система координат
    # xOy` -- переносна система координат -- вертикально орієнтований екран, рухається плоскопаралельно з корпусом дрона
    # Перетворення системи координат на екрані
    # Phi -- поворот Roll в градусах
    RPhi = GradToRad(Phi)
    x = xl*math.cos(RPhi) + yl*math.sin(RPhi) + Ra*math.sin(RPhi)
    y = -xl*math.sin(RPhi) + yl*math.cos(RPhi) - Ra*(1 - math.cos(RPhi))
    return x, y

def GetTargetXY(Phi):
    xl, yl = GetTargetPosition()
    x, y = ScreenTransformationXY(xl, yl, Phi)
    return x, y

def GetTrgetAccelerationXY(Phi):
    # Return the target image acceleration in pixels/sec2
    x0, y0 = GetTargetXY(Phi)
    t0 = date.datetime.now()
    x1, y1 = GetTargetXY(Phi)
    t1 = date.datetime.now()
    x2, y2 = GetTargetXY(Phi)
    t2 = date.datetime.now()
    dt1 = t1 - t0
    dt2 = t2 - t1
    vx0 = (x1 - x0)/dt1
    vy0 = (y1 - y0)/dt1
    vx1 = (x2 - x1)/dt2
    vy1 = (y2 - y1)/dt2
    ax = (vx1 - vx0)/dt2
    ay = (vy1 - vy0)/dt2
    return t2, x2, y2, vx1, vy1, ax, ay


def GetMachineState():
    Phi, Theta, Psi, St = GetBodyState()
    t, x, y, vx, vy, ax, ay = GetTrgetAccelerationXY(Phi)
    state = {"time": t, "x": x, "y": y, "vx": vx, "vy": vy, "ax": ax, "ay": ay, "roll": Phi, "pitch": Theta, "yaw": Psi, "Throttle": St}
    StateHistory.insert(0,state)
    StateHistory.pop(3)

def PrepareControllSignals():
    Phi, Theta, Psi, St = GetBodyState()
    GetMachineState(Phi)
    x0 = StateHistory[0]["x"]
    y0 = StateHistory[0]["y"]
    x1 = StateHistory[1]["x"]
    y1 = StateHistory[1]["y"]
    vx0 = StateHistory[0]["vx"]
    vy0 = StateHistory[0]["vy"]
    ax0 = StateHistory[0]["ax"]
    ay0 = StateHistory[0]["ay"]
    acc_x = -(3*vx0/2/dt+x0/dt/dt) - ax0
    acc_y = -(3*vy0/2/dt+y0/dt/dt) - ay0
    dec_x = vx0/2/dt + x0/dt/dt - acc_x
    dec_y = vy0/2/dt + y0/dt/dt - acc_y
    Kcor = (x1/(x1-x0) + y1/(y1-y0))/2
    Amax = Amax/Kcor
    dSt1 = (acc_x**2+acc_y**2)**0.5/Amax
    St1 = St + dSt1
    Phi1 = math.asin(acc_y/dSt1)
    dSt2 = (dec_x**2+dec_y**2)**0.5/Amax
    St2 = St + dSt2
    Phi2 = math.asin(dec_y/dSt2)
    return St1, Phi1, St2, Phi2, St, Phi
#endregion ============