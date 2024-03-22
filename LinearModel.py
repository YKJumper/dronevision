import math
import time
import random
import asyncio

#region ============ External Functions
def GetTargetPosition():
    # Return position of tracked object in local coordinates x`O`y`
    # xl yl = TrackObject(ObjectId)
    time.sleep(random.uniform(0.05, 0.07))
    x0=0
    y0=0
    vx=1
    vy=15
    ax=2
    ay=4
    t=time.time()
    dt = (t - __starttime)
    x1 = ax*dt**2/2+vx*dt+x0
    y1 = ay*dt**2/2+vy*dt+y0
    # print(dt, x1, y1)
    return x1, y1

def GetBodyState():
    # Return body orientation Roll, Pitch, Yaw and throttle level St in [0;1]
    return __Phi, __Theta, __Psi, __St

def SetBodyState(Phi, Theta, Psi, St):
    global __Phi, __Theta, __Psi, __St
    # Set body orientation Roll, Pitch, Yaw and throttle level St in [0;1]
    __Phi = Phi
    __Theta = Theta
    __Psi = Psi
    __St = St

def InitGuidingParameters():
    # Setinitial values of guiding paameters
    # Se (Dynamic) == the equilibrium position of throttle signal
    # Phie (Dynamic) == the equilibrium position of throttle signal
    Phi, Theta, Psi, St = GetBodyState()
    __St = 0.06
    __dt = 0.500
    Se = St
    Phie = Phi
    Theta0 = Theta
    Psi0 =  Psi
    GuideParams = {"deltatime": __dt, "__St": __St, "Phie": Phie, "Theta0": Theta0, "Psi0": Psi0, "Se": Se}
    return GuideParams
#endregion

#region ============ Auxilary Functions
def dist(am, bm):
    a = normMatrix(am)
    b = normMatrix(bm)
    n = min(len(a), len(b))
    d = 0
    for i in range(n):
        d += (a[i] - b[i])**2
    return d**0.5

def addVectors(am, bm):
    a = normMatrix(am)
    b = normMatrix(bm)
    n = min(len(a), len(b))
    d1 = []
    for i in range(n):
        d1.append(a[i] + b[i])
    return d1

def mltVectorReal(am, b):
    a = normMatrix(am)
    n = len(a)
    d = []
    for i in range(n):
        d.append(a[i]*b)
    return d

def mltVectors(am, bm):
    a = normMatrix(am)
    b = normMatrix(bm)
    n = min(len(a), len(b))
    d = []
    if n == 3:
        d.append(a[1] * b[2] - a[2] * b[1])
        d.append(a[2] * b[0] - a[0] * b[2])
        d.append(a[0] * b[1] - a[1] * b[0])
    return d

def mltVectorsScalar(am, bm):
    a = normMatrix(am)
    b = normMatrix(bm)
    n = len(a)
    nb = len(b)
    if n == nb:
        d = 0
        for i in range(n):
            d += a[i] * b[i]
    else:
        raise Exception('The vectors have different size.Unable to find scalar product.')
    return d

def absVector(a):
    return mltVectorsScalar(a, a)**0.5

def normVector(a):
    absa = absVector(a)
    if absa == 0:
        na = [0.0, 0.0, 0.0]
    else:
        na = mltVectorReal(a, 1/absa)
    return na

def GradToRad(degrees):
    radians = degrees/180*math.pi
    return radians

def RadToGrad(radians):
    degrees = radians/math.pi*180
    return degrees

def normMatrix(a):
    # Якщо матриця одновимірна: [[1,2,3]] чи [[1],[2],[3]] --> перетворити на вектор [1,2,3]
    m = len(a); n = 0
    if isinstance(a[0], list): n = len(a[0])
    if (m == 1) and (n >= 1):
        an = a[0]
        return an
    elif (m > 1) and (n == 1):
        an = [a[i][0] for i in range(m)]
        return an
    elif  (m > 1) and (n == 0):
        an = [a[i] for i in range(m)]
        return an
    elif  (m > 1) and (n > 1):
        return a
    else:
        raise Exception('The matrix can not be converted to a vector.')


def matrixToVector(a):
    # Якщо матриця одновимірна: [[1,2,3]] чи [[1],[2],[3]] --> перетворити на вектор [1,2,3]
    m = len(a); n = 0
    if isinstance(a[0], list): n = len(a[0])
    if (m == 1) or (n <= 1):
        return normMatrix(a)
    else:
        return a

def transposeMatrix(a):
    # a[m,n] = b[n,m]
    m = len(a); n = 0
    if isinstance(a[0], list): n = len(a[0])
    if n > 0:
        at = [[a[j][i] for j in range(m)] for i in range(n)]
    else:
        at = [[a[j]] for j in range(m)]
    return at

def mltMatrix(ap, bp):
    # a[m,n]x b[n,k] = c[m,k]
    a = matrixToVector(ap)
    b = matrixToVector(bp)
    m = len(a); n = 0
    nb = len(b); k = 0
    if isinstance(a[0], list): n = len(a[0])
    if isinstance(b[0], list): k = len(b[0])
    if n == nb:
        if k == 0:
            c = [mltVectorsScalar(a[l], [b[l] for l in range(n)]) for l in range(m)]
        else:
            c = [[mltVectorsScalar(a[i], [b[l][j] for l in range(n)]) for j in range(k)] for i in range(m)]
    else:
        raise Exception('The matrices have different sizes.')
    return c


def matrixGlob2Body(Theta, Phi, Psi, Alpha):
    # global __Alpha
    # Координати в локальній системі XaYaZa передворюються до глобальної XYZ
    # XYZ -- глобальна система координат
    # XaYaZa -- відносна система координат, повернута на кути Theta (Pitch), Phi (Roll), Psi (Yaw), з центром у векторі Ra 
    RTheta = GradToRad(Theta); RPhi = GradToRad(Phi); RPsi = GradToRad(Psi); RAlpha = GradToRad(Alpha)
    Cth = math.cos(RTheta); Cph = math.cos(RPhi); Cps = math.cos(RPsi); Cal = math.cos(RAlpha)
    Sth = math.sin(RTheta); Sph = math.sin(RPhi); Sps = math.sin(RPsi); Sal = math.sin(RAlpha)
    Ath = []
    Ath.append([1.0, 0.0, 0.0])
    Ath.append([0.0, Cth, Sth])
    Ath.append([0.0, -Sth, Cth])
    Aph = []
    Aph.append([Cph, 0.0, -Sph])
    Aph.append([0.0, 1.0, 0.0])
    Aph.append([Sph, 0.0, Cph])
    Aps = []
    Aps.append([Cps, Sps, 0.0])
    Aps.append([-Sps, Cps, 0.0])
    Aps.append([0.0, 0.0, 1.0])
    # Ur = [0.0, Cal, -Sal]
    Aal = [] # matrixRotationAxis(Phi, Ur)
    Aal.append([1.0, 0.0, 0.0])
    Aal.append([0.0, Cal, Sal])
    Aal.append([0.0, -Sal, Cal])
    A = mltMatrix(mltMatrix(mltMatrix(Aps, Aph), Ath), Aal)
    return A

def matrixRotationAxis(Theta, Ur):
    # Матриця повороту системи координа XYZ навколо вектора u на кут Theta
    RTheta = GradToRad(Theta); Cth = math.cos(RTheta); Sth = math.sin(RTheta)
    u = normVector(Ur)
    Ath = []
    Ath.append([Cth+u[0]*u[0]*(1-Cth), u[0]*u[1]*(1-Cth)+u[2]*Sth, u[0]*u[2]*(1-Cth)+u[1]*Sth])
    Ath.append([u[0]*u[1]*(1-Cth)-u[2]*Sth, Cth+u[1]*u[1]*(1-Cth), u[1]*u[2]*(1-Cth)-u[0]*Sth])
    Ath.append([u[0]*u[2]*(1-Cth)-u[1]*Sth, u[1]*u[2]*(1-Cth)+u[0]*Sth, Cth+u[2]*u[2]*(1-Cth)])
    return Ath

def matrixBody2Glob(Theta, Phi, Psi, Alpha):
    # global __Alpha
    # Координати в глобальній системі XYZ передворюються до локальної XaYaZa
    # XYZ -- глобальна система координат
    # XaYaZa -- відносна система координат, повернута на кути Theta (Pitch), Phi (Roll), Psi (Yaw), з центром у векторі Ra 
    A = matrixGlob2Body(Theta, Phi, Psi, Alpha)
    B = transposeMatrix(A)
    return B

def ScreenTransformationXY(xl, yl, Phi):
    # xlOlyl -- система координат камери, Ol -- верхній лівий кут, в якій трекер повертає координати цілі
    # xl -- координата по горизонталі вправа, yl -- координата по вертикалі вниз
    # (__Xc, __Yc) -- координати центру екрану
    # (0, -__Ra) -- центр обертання екрану
    # xrOryr -- система координат з центром Or в центрі екрану
    # xr -- координата по горизонталі вправа, yr -- координата по вертикалі вгору
    # xOy -- вертикально орієнтований екран, рухається плоскопаралельно з корпусом дрона
    # Перетворення системи координат на екрані
    # Phi -- поворот Roll в градусах
    global __Xc, __Yc, __Ra
    RPhi = GradToRad(Phi); Cph = math.cos(RPhi); Sph = math.sin(RPhi)
    xr = (xl - __Xc); yr = (__Yc -yl)
    x = xr*Cph + yr*Sph + __Ra*Sph
    y = -xr*Sph + yr*Cph - __Ra*(1 - Cph)
    return x, y

#endregion ===============================

#region ============ Guiding Functions
def GetTargetScreenXYMtrx(Theta, Phi, Psi, Alpha, Rd, Rt):
    global __SRes, __Focus35
    # Матриця перетворення глобальних координат в координати вертикально орієнтованого екрану
    As = matrixBody2Glob(Theta, Phi, Psi, Alpha)
    # Координати цілі в системі координат екрану
    Rst = normMatrix(mltMatrix(As, addVectors(Rt, mltVectorReal(Rd, -1.0))))
    # Проекція на площину екрану
    Rzx = addVectors(Rst, [0.0, -1.0*Rst[1], 0.0])
    nRzx = normVector(Rzx)
    # Кут між віссю екрану і напрямком на ціль, градусів
    nRst = normVector(Rst)
    Beta = math.acos(nRst[1])
    # Координати цілі в пікселях
    Rscreen = mltVectorReal(nRzx, __Focus35*__SRes*math.tan(Beta))
    return Rscreen

def GetTargetScreenXY(Theta, Phi, Psi, Alpha, Rd, Rt):
    global __SRes, __Focus35
    RTheta = GradToRad(Theta); RPhi = GradToRad(Phi); RPsi = GradToRad(Psi); RAlpha = GradToRad(Alpha)
    Cth = math.cos(RTheta); Cph = math.cos(RPhi); Cps = math.cos(RPsi); Cal = math.cos(RAlpha)
    Sth = math.sin(RTheta); Sph = math.sin(RPhi); Sps = math.sin(RPsi); Sal = math.sin(RAlpha)
    Yb = [0.0, 1.0, 0.0]
    # Система координат екрану
    Yal = [Sal*Sph, Cal, Sal*Cph]
    Xal = [1.0, 0.0, 0.0]
    Zal = [0.0, 0.0, 1.0]
    if Alpha != 0: Xal = normVector(mltVectors(Yb, Yal))
    if Alpha != 0: Zal = normVector(mltVectors(Xal, Yal))
    # Матриця перетворення глобальних координат в координати вертикально орієнтованого екрану
    As = matrixGlob2Body(Theta, 0.0, 0.0, 0.0)
    # Координати цілі в системі координат дрона
    Rxy = addVectors(Rt, mltVectorReal(Rd, -1.0))
    Rat = normMatrix(mltMatrix(As, Rxy))
    # Проекція на площину екрану
    Rst = [mltVectorsScalar(Xal, Rat), mltVectorsScalar(Yal, Rat), mltVectorsScalar(Zal, Rat)]
    nRst = normVector(Rst)
    # Кут між віссю екрану і напрямком на ціль, градусів
    Beta = math.acos(nRst[1])
    # Координати цілі в пікселях
    Rscreen = mltVectorReal(nRst, __Focus35*__SRes*math.tan(Beta))
    return [Rscreen[0], Rscreen[2]]

def GetTrgetAccelerationXY(Phi):
    # Return the target image acceleration in pixels/sec2
    x0, y0 = GetTargetXY(Phi)
    t0 = time.time()
    x1, y1 = GetTargetXY(Phi)
    t1 = time.time()
    x2, y2 = GetTargetXY(Phi)
    t2 = time.time()
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
    state = {"time": t, "x": x, "y": y, "vx": vx, "vy": vy, "ax": ax, "ay": ay, "roll": Phi, "pitch": Theta, "yaw": Psi, "throttle": St}
    __StateHistory.insert(0,state)
    if len(__StateHistory) > 3:
        __StateHistory.pop(3)
    else:
        for i in range(2):
            Phi, Theta, Psi, St = GetBodyState()
            t, x, y, vx, vy, ax, ay = GetTrgetAccelerationXY(Phi)
            state = {"time": t, "x": x, "y": y, "vx": vx, "vy": vy, "ax": ax, "ay": ay, "roll": Phi, "pitch": Theta, "yaw": Psi, "throttle": St}
            __StateHistory.insert(0,state)
        

def PrepareControllSignals():
    global __St, __Ka
    Phie, Theta, Psi, Ste = GetBodyState()
    GetMachineState()
    dt = __StateHistory[0]["time"] - __StateHistory[1]["time"]
    r0 = [__StateHistory[0]["x"], __StateHistory[0]["y"]]
    v0 = [__StateHistory[0]["vx"], __StateHistory[0]["vy"]]
    a0 = [__StateHistory[0]["ax"], __StateHistory[0]["ay"]]
    a1 = [__StateHistory[1]["ax"], __StateHistory[1]["ay"]]
    St0 = __StateHistory[0]["throttle"]
    St1 = __StateHistory[1]["throttle"]
    r = absVector(r0)
    da = absVector(a0) - absVector(a1)
    v = absVector(v0)
    if St0 != St1:
        __Ka = da/(St0-St1)
    # Встановлюємо Roll -- ціль має бути по осі OYr
    if r == 0:
        Phi1 = 0
    else:
        Phi1 = RadToGrad(math.asin(r0[0]/r))
    if Phi1 > __Phi_max:
        Phi1 = __Phi_max
    if Phi1 < -__Phi_max:
        Phi1 = -__Phi_max
    
    # Коригуємо тягу -- dSt. рахуємо зміну тяги
    dSt = -(r0[1]/dt + v)/2/__Ka/dt
    St = Ste + dSt
    if St > 1:
        St = 1
    if St < 0:
        St = 0
    
    # Встановлюємо значення параметрів після корекції
    Ste = (Ste + St)/2
    Phie = Phi1
    return St, Phi1, Ste, Phie
#endregion ============

if __name__ == "__main__":
    # Drone's body position
    __Phi = 16
    __Theta = -25
    __Psi = 0
    # Camera configuration
    __Alpha = 15 # Camera elevation angle over drone's body
    __Focus35 = 22 # Focal length (35mm equiv.)
    __Width = 1080 #Camera matrix sensor width, pixels
    __SRes = __Width/35 # Matrix equivalent resolution (pixels/mm)
    __Ra = -__Focus35*__SRes*math.tan(GradToRad(__Alpha)) # Rotation center coordinates in xOy (0,-__Ra)
    # Координати дрона в глобальних координатах
    __Rd = [0.0, 0.0, 150.0]
    # Координати цілі в глобальних координатах (розраховуються, щоб бути близько центру екрану)
    __Y =__Rd[2]/(math.tan(GradToRad(__Theta + __Alpha)))
    if __Y < 0: __Y = -__Y
    __Rt = [0.0, __Y+100, 0.0]
    Rscreen = GetTargetScreenXY(__Theta, __Phi, __Psi, __Alpha, __Rd, __Rt)
    print(Rscreen)
    Rscreen0 = GetTargetScreenXY(__Theta, 0.0, __Psi, __Alpha, __Rd, __Rt)
    print(Rscreen0)
    # # Координати цілі в системі координат екрану
    # __Rst = normMatrix(mltMatrix(As, addVectors(__Rt, mltVectorReal(__Rd, -1.0))))
    # __Rzx = addVectors(__Rst, [0.0, -1.0*__Rst[1], 0.0])
    # __nRst = normVector(__Rst)
    # Beta = RadToGrad(math.acos(__nRst[1]))
    # __Rscreen = mltVectorReal(__nRst, Beta)

    __St = 0.6
    # Roll angle limit 
    __Phi_max = 55
    __Ka = 1000
    __St = 0.6
    __StateHistory = [] # Sate history list
    __starttime=time.time()
    # InitGuidingParameters()
    # for i in range(3):
    #     St, Phi1, Ste, Phie = PrepareControllSignals()
    #     SetBodyState(Phi1, __Theta, __Psi, St)
    #     print(St, Phi1, Ste, Phie)
    print ('The End')