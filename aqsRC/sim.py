#sim
from math import exp
from pprint import pprint as pp
from aqsRC.main3 import Sensor

def get_u(rs=4.7e3,cs=150e-12,r0=4.7e3, rout=320e3, cout=100e-9, dt=1/80e6*7*2, aimax=1024):
        ud =.2
        u0=3.3
        du=u0/aimax

        us1=u0*rs/(rs+r0) # @sensor
        u1=u0*rs/(rs+r0) - ud #measure
        '''
        u1=u0*rs/(rs+r0) - ud
        (u1+ud)*(rs+r0)=u0*rs
        (u1+ud)*r0=u0*rs - (u1+ud)*rs 
        (u1+ud)*r0=rs*(u0 - u1-ud) 
        
        rs= (u1+ud)*r0/(u0 - (u1+ud) )
        -------------
        (u0-urest)*e^-dt/T = urest #wg. symmetrie
        u0*e^ = urest(1+e^)
        u0 - urest = u0 - u0*e/(1+e)
        u=u0*(1-e/(1+e))
        =u0(1+e -e)/(1+e)
        u=u0/(1+e^-dt/T)  # us max
        '''
        r0s=r0*rs/(r0+rs) #r0||rs
        # usf=us1/(1+exp(-dt/(r0s*cs)))
        # uf = usf-ud
        
        uf=(u0*rs/(rs+r0))/(1+exp(-dt/(r0*rs/(r0+rs)*cs))) - ud
        
        aif=int(uf/du)
        ai1=int(u1/du)
        
        return uf, u1, aif, ai1


def mk_data():
    
    data=[]
    rss=[1, 1.5, 2.2, 4.7, 5.7, 10]
    css=[20, 56, 100, 156, 220]
    
    for r in rss:
        for c in css:
            u=get_u(rs=r*1e3,cs=c*1e-12)
            data.append([r,c,u[2], u[3]])
    
    return data

def test():
    
    u=get_u(rs=4.7*1e3,cs=120*1e-12)
    print(u)
    s=Sensor(name='t')
    s.add(u[2],u[3])
    print(s.print())

if __name__ == '__main__':
    
    test()
    
    pp(mk_data())
    # print(get_u(rs=5*1e3,cs=120*1e-12))

    pass





