from math import exp

from sensor_data import sensors
from math import log
from pprint import pprint as pp
import numpy as np

from scipy.interpolate import SmoothBivariateSpline

from mhLib.PlotJson import Plot


from main3 import Sensor
# class Sensor():
#
#     def __init__(self, name='aqs5'):
#     # def __init__(self, name='sim'):
#         self.name=name
#         self.aqs=sensors[name]
#
#         self.data = np.array(self.aqs['cal'])
#
#         self.measures = self.data[:, 2:]
#         self.Ufs =self.data[:, 2]
#         self.U1s =self.data[:, 3]
#         self.Rs = self.data[:, 0]
#         self.Cs = self.data[:, 1]
#         self.Ts = self.data[:, 0] * self.data[:, 1]
#         self.usf_errs = np.zeros(len(self.data))
#         self.us1_errs = np.zeros(len(self.data))
#
#         self.u0 = 3.3
#         self.r0 = self.aqs['params']['r0'] * 1e3
#         self.rout = self.aqs['params']['rout'] * 1e3
#         self.dt = self.aqs['params']['dt']
#         self.du = self.aqs['params']['du']
#
#         self.ud = 0. #.2
#
#         # for i in range(len(self.data)):
#         #     # self.usfs[i], self.us1s [i]=self.calc_err_usf_us0 (self.data[i][0], self.data[i][1])
#         #     self.usf_errs[i], self.us1_errs [i] = self.calc_err_usf_us1 (self.data[i])
#
#         self.spline_cs = SmoothBivariateSpline(self.data[:, 2], self.data[:, 3], self.data[:, 1], kx=3, ky=2)
#         self.spline_rs = SmoothBivariateSpline(self.data[:, 2], self.data[:, 3], self.data[:, 0], kx=2, ky=2)
#
#
#         self.k_avg=20.
#
#         self.cnt=0
#
#         self.u1 = 0
#         self.uf = 0
#
#         self.rs=0
#         self.T=0
#         self.cs=0
#
#         self.rs_avg=self.rs
#         self.cs_avg=self.cs
#         self.u1_avg=self.u1
#         self.uf_avg=self.uf
#         self.T_avg=self.T
#         self.sigma_rs=0
#         self.sigma_cs=0
#         self.sigma_T=0
#
#     def get_r0_rech(self):
#         pass
#     def calc_cs(self):
#
#         self.calc_T()
#         self.calc_rs()
#         r= self.rs*self.r0/(self.rs+self.r0)
#         self.cs = self.T /r
#
#         pass
#     def calc_T(self):
#         '''
#         yt = y0* exp(-t/T)
#         log(yt)=log(y0)-t/T
#         t/T = log(y0)-log(yt)
#         T=t/(log(y0)-log(yt))
#         '''
#         # calulated for falling edge, symmetrie assumed
#         # self.T = self.dt / (log(self.uf+self.ud) - log(self.u1-self.uf))
#         u1=self.u1+self.ud
#         uf=self.uf+self.ud
#         # self.T = self.dt / (log(u1) - log(u1-uf))
#         try:
#             # self.T = self.dt / (log(uf) - log(u1-uf))  
#             self.T = self.dt / log(uf/(u1-uf))  
#         except:
#             print(uf, u1-uf)
#             print(self.aif, self.ai1)
#             # print(e)
#
#         print (uf, u1-uf)
#
#
#     def calib_u1(self, rs):   
#
#         u1=self.u0*rs/(rs+self.r0)-self.ud
#
#         return u1         
#
#     def calc_rs(self):
#
#         i0 = (self.u0 - self.us1) / self.r0
#         irout = self.u1 / self.rout 
#         irs = i0 - irout
#         self.rs = self.us1 / irs
#
#         # uf=(u0*rs/(rs+r0))/(1+exp(-dt/(r0*rs/(r0+rs)*cs))) - ud
#
#     def add(self,aif,ai1):
#         self.cnt+=1
#
#         self.aif=aif
#         self.ai1=ai1
#
#         self.uf=aif*self.aqs['params']['du']
#         self.u1=ai1*self.aqs['params']['du']
#
#         self.rs = self.spline_rs(self.aif,self.ai1)[0][0]
#         self.cs = self.spline_cs(self.aif,self.ai1)[0][0]
#
#         self.T= self.rs * self.cs
#
#         self.rs_avg=(self.rs_avg*(self.k_avg-1) + self.rs)/self.k_avg
#         self.cs_avg=(self.cs_avg*(self.k_avg-1) + self.cs)/self.k_avg
#         self.u1_avg=(self.u1_avg*(self.k_avg-1) + self.u1)/self.k_avg
#         self.uf_avg=(self.uf_avg*(self.k_avg-1) + self.uf)/self.k_avg
#         self.T_avg=(self.T_avg*(self.k_avg-1) + self.T)/self.k_avg
#
#         d = sqrt((self.rs - self.rs_avg)**2)
#         self.sigma_rs=(self.sigma_rs*(self.k_avg-1) + d)/self.k_avg
#         d = sqrt((self.cs - self.cs_avg)**2)
#         self.sigma_cs=(self.sigma_cs*(self.k_avg-1) + d)/self.k_avg
#         d = sqrt((self.T - self.T_avg)**2)
#         self.sigma_T=(self.sigma_T*(self.k_avg-1) + d)/self.k_avg
#
#     def toString(self):
#         s = "\nname = " + self.name + '\n'
#         s += "C = " + str(self.cs) + '\n'
#         s += "R = " + str(self.rs) + '\n'
#         s += "T = " + str(self.T) + '\n'
#         s += "uf = " + str(self.uf) + '\n'
#         s += "u1 = " + str(self.u1) + '\n'
#
#         s += "C_avg = " + str(self.cs_avg) + '\n'
#         s += "R_avg = " + str(self.rs_avg) + '\n'
#         s += "T_avg= " + str(self.T_avg) + '\n'
#         s += "u1_avg = " + str(self.u1_avg) + '\n'
#         s += "uf_avg= " + str(self.uf_avg) + '\n'
#         s += "sigma_rs " + str(self.sigma_rs/1e3) + '\n'
#         s += "sigma_cs= " + str(self.sigma_cs*1e12) + '\n'
#         s += "sigma_T= " + str(self.sigma_T) + '\n'
#
#         return s
#
#     def print(self):
#         s=self.toString()
#         print (s)
#
#     def reset(self,aif, ai1):
#         self.cnt=0
#         self.add(aif, ai1)
#
#         self.rs_avg=self.rs
#         self.cs_avg=self.cs
#         self.u1_avg=self.u1
#         self.uf_avg=self.uf
#         self.T_avg=self.T
#
#         self.sigma_rs=0
#         self.sigma_cs=0
#         self.sigma_T=0
#
#
#     def publishMQTT(self):
#
#         publish.single(self.name +"/aif",self.aif, hostname=mqtt_host)
#         publish.single(self.name +"/ai1",self.ai1, hostname=mqtt_host)
#         publish.single(self.name +"/uf",self.uf, hostname=mqtt_host)
#         publish.single(self.name +"/u1",self.u1, hostname=mqtt_host)
#         publish.single(self.name +"/u1_avg",self.u1_avg, hostname=mqtt_host)
#         publish.single(self.name +"/uf_avg",self.uf_avg, hostname=mqtt_host)
#         publish.single(self.name +"/R",self.rs, hostname=mqtt_host)
#         publish.single(self.name +"/C",self.cs, hostname=mqtt_host)
#         publish.single(self.name +"/Ravg",self.rs_avg, hostname=mqtt_host)
#         publish.single(self.name +"/Cavg",self.cs_avg, hostname=mqtt_host)
#         publish.single(self.name +"/T",self.T, hostname=mqtt_host)
#
#         publish.single(self.name +"/sigma_R",self.sigma_rs, hostname=mqtt_host)
#         publish.single(self.name +"/sigma_C",self.sigma_cs, hostname=mqtt_host)
#         publish.single(self.name +"/sigma_T",self.sigma_T*1e9, hostname=mqtt_host)
        
s=Sensor(name='aqs6')

def test_r2u_1():
    pass
    
    

def get_u(rs=4.7e3,cs=150e-12,r0=4.7e3, rout=320e3, cout=100e-9, dt=1/80e6*7, aimax=1024):
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

def test2():
    s = Sensor('aqs1')

    us=[
            [0.541,    0.675],
            [0.553,    0.688],
            [0.566,    0.697],
            [0.581,    0.716],
            [0.603,    0.741],
            [0.625,    0.769],
            [0.666,    0.809],
            [0.675,    0.819],
        ]
    
    for u in us:
        r=s.spline_rs(u[0]/s.du,u[1]/s.du)[0][0]
        r2=s.spline_rs((u[1]-.1)/s.du,u[1]/s.du)[0][0]
        print(r, ', ', r2)
    
    pass
    
def get_interp(nam):
    s = Sensor(nam)
    l={}
    for u in np.arange(1,2.7,.1):
        # r=s.spline_rs(self.aif,self.ai1)[0][0]
        r=s.spline_rs((u-.5)/s.du,u/s.du)[0][0]
        l[r]=u
    return l

def get_lines(nam):
    s = Sensor(nam)
    Rs = s.Rs
    U1s= s.u1s*s.du
    Ufs= s.ufs*s.du
    # cal_ai1s = np.array([int(s.calib_u1(rs*1e3)/s.du) for rs in s.Rs])
    cal_u1s = np.array([s.calc_rs2us1(rs) for rs in s.Rs])
    
    l1 = {}
    l2 = {}
    l3 = {}
    d1 = {}
    d2 = {}
    d3 = {}
    
    for i in range(len(Rs)):
        # if s.Cs[i]==100:
            l1[float(Rs[i])] = (cal_u1s[i])
            l2[float(Rs[i])] = (U1s[i])
            l3[float(Rs[i])] = (Ufs[i])
            
            # d1[float(Rs[i])] = int(cal_u1s[i]-U1s[i])
            d2[float(Rs[i])] = (cal_u1s[i]-U1s[i])
            d3[float(Rs[i])] = (cal_u1s[i]-Ufs[i])
        
            print(Rs[i], ' ', round(Ufs[i]*s.du,3)) #for compare with ltspice
        
    dicdb = [[l1, l2, l3], [ d2, d3],  ]
    print (dicdb)
    Plot.writeJson2(dicdb=dicdb)
    
    pp(cal_u1s)
    pp(Rs)
    pp(U1s)
    pp(Ufs)

    return dicdb

def test():
    
    # lines_t = [[{1:1,10:2}, {1:2,10:3}], [{1:2,10:3}]]
    # lines_t1 = [[{1.5:1.5,10:2}, {1:2,10:3}], [{1:2,10:3}]]
    
    lines_1 = get_lines('aqs1')
    lines_5 = get_lines('aqs5')
    lines_6 = get_lines('aqs6')
    lines_8 = get_lines('aqs8')
    
    lines_1_interpolated = get_interp('aqs1')
    lines_5_interpolated = get_interp('aqs5')
    lines_6_interpolated = get_interp('aqs6')
    lines_8_interpolated = get_interp('aqs8')

    lines=[]
    # lines=[lines_t[0]+lines_t1[0]]#, lines_t[1]]
    lines.append(lines_1[0])#+ lines_2[0])# + lines_3[0] )  #, [lines_1[0]] ]#, lines_1[1]+ lines_2[1]]

    lines[0].append(lines_1_interpolated)
    # lines[0].append(lines_2[0][1])
    # lines[0].append(lines_2[0][2])
    # lines[0].append(lines_3[0][1])
    # lines[0].append(lines_3[0][2])
    
    
    # lines=[lines_1[0]+ lines_2[0]+ lines_3[0], lines_1[1]+ lines_2[1]+ lines_3[1]]
    
    Plot.writeJson2(dicdb=lines)
    
    return
    # s = Sensor('aqs8')
    Rs = s.Rs
    U1s= s.u1s*s.du
    Ufs= s.ufs*s.du
    # cal_ai1s = np.array([int(s.calib_u1(rs*1e3)/s.du) for rs in s.Rs])
    cal_u1s = np.array([s.calc_rs2us1(rs) for rs in s.Rs])
    
    l1 = {}
    l2 = {}
    l3 = {}
    d1 = {}
    d2 = {}
    d3 = {}
    
    for i in range(len(Rs)):
        # if s.Cs[i]==100:
            l1[float(Rs[i])] = (cal_u1s[i])
            l2[float(Rs[i])] = (U1s[i])
            l3[float(Rs[i])] = (Ufs[i])
            
            # d1[float(Rs[i])] = int(cal_u1s[i]-U1s[i])
            d2[float(Rs[i])] = (cal_u1s[i]-U1s[i])
            d3[float(Rs[i])] = (cal_u1s[i]-Ufs[i])
        
            print(Rs[i], ' ', round(Ufs[i]*s.du,3)) #for compare with ltspice
        
    dicdb = [[l1, l2, l3], [ d2, d3],  ]
    print (dicdb)
    Plot.writeJson2(dicdb=dicdb)
    
    pp(cal_u1s)
    pp(Rs)
    pp(U1s)
    pp(Ufs)



if __name__ == '__main__':
    test()
    pass