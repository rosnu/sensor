import socket
import datetime
import json
# import requests
# import time
# import mhLib.Avg
# import math
from math import exp,log,sqrt
import numpy as np
# import mhLib.send_webde
# from mhlib.Avg import Avg
# import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

from scipy.interpolate import SmoothBivariateSpline

from sensor_data import sensors

class Avg():
    def __init__(self, m_max=1e10): # equal waighted till..
        self.m_max=m_max
        self.m=0
        self.val=0
        self.diff=0
        
    def add(self, val=0):  # 
        
        if self.m<self.m_max: self.m+=1
        self.diff=(val -self.val)/self.m
        self.val+=self.diff
        
class Sensor():

    def __init__(self, name='aqs5'):
        self.name=name
        self.aqs=sensors[name]

        self.data = np.array(self.aqs['cal'])
    
        self.measures = self.data[:, 2:]
        self.ufs=self.data[:, 2]
        self.u1s=self.data[:, 3]
        self.Rs = self.data[:, 0]
        self.Cs = self.data[:, 1]
        # self.Ts = self.data[:, 0] * self.data[:, 1]
        self.usf_errs = np.zeros(len(self.data))
        self.us1_errs = np.zeros(len(self.data))

        self.u0 = 3.3
        self.r0 = self.aqs['params']['r0'] * 1e3
        self.rout = self.aqs['params']['rout'] * 1e3
        self.dt = self.aqs['params']['dt']
        self.du = self.aqs['params']['du']
        
        # for i in range(len(self.data)):
        #     # self.usfs[i], self.us1s [i]=self.calc_err_usf_us0 (self.data[i][0], self.data[i][1])
        #     self.usf_errs[i], self.us1_errs [i] = self.calc_err_usf_us1 (self.data[i])

        # self.spline_cs = SmoothBivariateSpline(self.data[:, 2], self.data[:, 3], self.data[:, 1], kx=2, ky=2)
        # self.spline_rs = SmoothBivariateSpline(self.data[:, 2], self.data[:, 3], self.data[:, 0], kx=2, ky=2)
        self.spline_cs = SmoothBivariateSpline(self.ufs, self.u1s, self.Cs, kx=2, ky=2)
        self.spline_rs = SmoothBivariateSpline(self.ufs, self.u1s, self.Rs, kx=2, ky=2)
                
        self.m_avg=5.

        self.cnt=0
        self.cycle=0
        self.dcycle=0
       
        self.u1 = 0
        self.uf = 0
        
        self.rs=0
        self.T=0
        self.Ts=0
        self.cs=0
               
        self.rs_avg=Avg(self.m_avg)
        self.cs_avg=Avg(self.m_avg)
        self.u1_avg=Avg(self.m_avg)
        self.uf_avg=Avg(self.m_avg)
        self.T_avg=Avg(self.m_avg)
        self.Ts_avg=Avg(self.m_avg)
        # self.sigma_rs=0
        # self.sigma_cs=0
        # self.sigma_T=0
        
    def add(self,aif,ai1):
        self.cnt+=1
        
        self.aif=aif
        self.ai1=ai1
        
        self.uf=aif*self.aqs['params']['du']
        self.u1=ai1*self.aqs['params']['du']
        
        self.rs = self.spline_rs(self.aif,self.ai1)[0][0]
        self.cs = self.spline_cs(self.aif,self.ai1)[0][0]
      
        self.T= self.rs * self.cs
        self.Ts= self.rs*self.r0*1e-3/(self.rs+self.r0*1e-3) * self.cs
        
        self.rs_avg.add(self.rs)
        self.cs_avg.add(self.cs)
        self.u1_avg.add(self.u1)
        self.uf_avg.add(self.uf)
        self.T_avg.add(self.T)
        self.Ts_avg.add(self.Ts)
        
        # d = sqrt((self.rs - self.rs_avg)**2)
        # self.sigma_rs=(self.sigma_rs*(self.k_avg-1) + d)/self.k_avg
        # d = sqrt((self.cs - self.cs_avg)**2)
        # self.sigma_cs=(self.sigma_cs*(self.k_avg-1) + d)/self.k_avg
        # d = sqrt((self.T - self.T_avg)**2)
        # self.sigma_T=(self.sigma_T*(self.k_avg-1) + d)/self.k_avg
    
    def toString(self):
        s = "\nname = " + self.name + '\n'
        s += "cycle = " + str(self.cycle) + '\n'
        s += "C = " + str(self.cs) + '\n'
        s += "R = " + str(self.rs) + '\n'
        s += "T = " + str(self.T) + '\n'
        s += "Ts = " + str(self.Ts) + '\n'
        s += "uf = " + str(self.uf) + '\n'
        s += "u1 = " + str(self.u1) + '\n'
        
        s += "C_avg = " + str(self.cs_avg.val) + '\n'
        s += "R_avg = " + str(self.rs_avg.val) + '\n'
        s += "T_avg= " + str(self.T_avg.val) + '\n'
        s += "u1_avg = " + str(self.u1_avg.val) + '\n'
        s += "uf_avg= " + str(self.uf_avg.val) + '\n'
        # s += "sigma_rs " + str(self.sigma_rs/1e3) + '\n'
        # s += "sigma_cs= " + str(self.sigma_cs*1e12) + '\n'
        # s += "sigma_T= " + str(self.sigma_T) + '\n'
     
        return s
    
    def toJson(self):
    
        payload = {
            "aif": self.aif,
            "ai1": self.ai1,
            "uf" : round(self.uf,3),
            "uf_avg" : round(self.uf_avg.val,3),
            "u1" : round(self.u1,3),
            "u1_avg" : round(self.u1_avg.val,3),
            "R" : round(self.rs,3),
            "C" : round(self.cs,1),
            "C_avg" : round(self.cs_avg.val,1),
            "T" : round(self.T,1),
            "T_avg" : round(self.T_avg.val,1),
            "Ts" : round(self.Ts,1),
            "Ts_avg" : round(self.Ts_avg.val,1),
            "dcycle" : self.dcycle,
            
            }

        return json.dumps(payload)
    
    
    def print(self):
        s=self.toString()
        print (s)
    
    def reset(self,aif, ai1):
        self.cnt=0
        self.add(aif, ai1)
        
        self.rs_avg.m=0
        self.cs_avg.m=0
        self.u1_avg.m=0
        self.uf_avg.m=0
        self.T_avg.m=0

    def calc_rs2us1(self, rs=1): # for test only
        us1=self.u0 * rs/(rs+self.r0/1000)
        return us1

if __name__ == '__main__':
    
    aqs5=sensors['aqs5']
    
    pass