import math
from math import exp, log

class Calc():

    def __init__(self, ai0=630, aif=440, dt=7 / 80e6):
        self.u = 3.3
        self.i2u = 3.3 / 1024
        
        self.u0 = ai0 * self.i2u
        self.uf = aif * self.i2u
        self.r0 = 4.7e3
        self.rout = 320e3
        self.cout = 10e-9
        self.ud = .4
        self.dt = dt
        
        # to calculate
        self.urs=0
        self.rs=0
        self.cs=0
        self.T=0
        self.fc=0 
        
        self.calc_C()

    def calc_C(self):
    
        self.calc_T()
        self.calc_rs()
        self.cs = self.T / (self.rs*self.r0/(self.rs+self.r0))
    
    def calc_T(self):
        '''
        yt = y0* exp(-t/T)
        log(yt)=log(y0)-t/T
        t/T = log(y0)-log(yt)
        T=t/(log(y0)-log(yt))
        '''
        # calulated for falling edge, symmetrie assumed
        self.T = self.dt / (log(self.uf+self.ud) - log(self.u0-self.uf))
    
    def calc_rs(self):
               
        urs = self.u0 + self.ud
        irout = self.u0 / self.rout 
        i0 = (self.u - urs) / self.r0
        irs = i0 - irout
        self.rs = urs / irs
    
    def toString(self):
        s = "C = " + str(self.cs) + '\n'
        s += "R = " + str(self.rs) + '\n'
        s += "T = " + str(self.T) + '\n'
        s += "u0 = " + str(self.u0) + '\n'
        s += "uf = " + str(self.uf) + '\n'
        
        return s
    
    def print(self):
        print (self.toString())
    
    
def calc(u0=1.8, uf=1.25, dt=7 / 80e6):  # dt us

    du = u0 - uf 
    T = calc_T(y0=uf, yt=du, t=dt)
    rs = calc_rs(uf)
    cs = T / rs
    return cs


def calc_T(y0=1, yt=exp(-1), t=1):
    
    # yt = y0* exp(-t/T)
    # log(yt) = log(..
    # log(yt)=log(y0)-t/T
    # t/T = log(y0)-yt
    T = t / (log(y0) - log(yt))

    return T
 
    
def sim(u0=1, T=1, t=1,):
    
    u = u0 * math.exp(-t / T)
    return u


def test2():
    r = (4700 * 9700) / (4700 + 9700)
    c = 17e-12
    T = r * c 
    print('T ', T)

    t = 7 / 80e6

    u0 = 1.86
    u = u0 * math.e ** (-t / T)

    print ('u ', u)
    
    Tcalc = calc_T(u0, u, t)
    
    print ('Tcalc', Tcalc)
    
    c = Tcalc / r
    print(c)


def test():
    
    dt = 1. 
    cs = 1.
    rs = 1.
    u0 = 1.
    uf = sim()
    
    T = calc_T(u0=u0, uf=uf, dt=dt)
    cs = calc(u0=u0, uf=uf, dt=dt)
    print('cs' , cs)


def calc_rs(uout):
    
    u = 3.3
    r0 = 4.7e3
    rout = 320e3
    ud = .4
    
    urs = uout + ud
    iout = uout / rout 
    i0 = (u - urs) / r0
    irs = i0 - iout
    rs = urs / irs
   
    return rs
    

def test3():
    ai0 = 630
    aif = 440
    i2u = 3.3 / 1024
    
    u0 = ai0 * i2u
    uf = aif * i2u
    print('u0 ', u0)
    print('uf ', uf)
    ud = .4
    
    urc0 = u0 + ud
    urcf = uf + ud
    print('urc0 ', urc0)
    print('urcf ', urcf)
    
    # i0=(3.3-urc0)/4.7e3
    # print('i0 ', i0)
    # rs=u0/i0
    # print('rs ', rs)
    
    rs = calc_rs(u0)
    print('rs ', rs)
    
    rr = rs * 4.7e3 / (rs + 4.7e3)
    print('rr ', rr)
    
    T = calc_T(urc0, urcf, 7 / 80e6)
    print('T ', T)
    c = T / rr
    print('c ', c)


if __name__ == '__main__':
    c = Calc()
    c.print()
    test3()
    exit()
    cs = calc(u0=1.86, uf=0.38, dt=7 / 80e6)
    print(cs)

