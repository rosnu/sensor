import socket
import datetime
import json
import requests
import time
# import mhLib.Avg
import math
from math import exp,log,sqrt
import numpy
# import mhLib.send_webde
# from mhlib.Avg import Avg
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from numpy.random.tests.test_smoke import params_0

sensors_C={'aqs0':30,'aqs1':30,'aqs2':30,'aqs3':30,'aqs4':30, }

params = {'aqs0':{'u':3.3, 'frq':5000, }, 
          'aqs1':{'u':3.3, 'frq':5000, }, 
          'aqs2':{'u':3.3, 'frq':5000, }, 
          'aqs3':{'u':3.3, 'frq':5000, }, 
          'aqs4':{'u':3.3, 'frq':5000, }, 
        }

class SensorInt():

    def __init__(self, name='aqs6' ):

        
        
        self.k_avg=50.
        self.rs_avg=self.rs
        self.cs_avg=self.cs
        self.u0_avg=self.u0
        self.uf_avg=self.uf
        self.T_avg=self.T
        self.sigma_rs=0
        self.sigma_cs=0
        self.sigma_T=0

    def add(self,ai0,aif):
        self.ai0=ai0
        self.aif=aif
        self.cnt+=1
        self.u0 = ai0 * self.i2u
        self.uf = aif * self.i2u
        
        self.calc_cs()
        
        self.rs_avg=(self.rs_avg*(self.k_avg-1) + self.rs)/self.k_avg
        self.cs_avg=(self.cs_avg*(self.k_avg-1) + self.cs)/self.k_avg
        self.u0_avg=(self.u0_avg*(self.k_avg-1) + self.u0)/self.k_avg
        self.uf_avg=(self.uf_avg*(self.k_avg-1) + self.uf)/self.k_avg
        self.T_avg=(self.T_avg*(self.k_avg-1) + self.T)/self.k_avg
        
        d = sqrt((self.rs - self.rs_avg)**2)
        self.sigma_rs=(self.sigma_rs*(self.k_avg-1) + d)/self.k_avg
        d = sqrt((self.cs - self.cs_avg)**2)
        self.sigma_cs=(self.sigma_cs*(self.k_avg-1) + d)/self.k_avg
        d = sqrt((self.T - self.T_avg)**2)
        self.sigma_T=(self.sigma_T*(self.k_avg-1) + d)/self.k_avg
        
    def calc_cs(self):
    
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
        s = "name = " + self.name + '\n'
        s += "ai0 = " + str(self.ai0) + '\n'
        s += "aif = " + str(self.aif) + '\n'
        s += "C = " + str(self.cs) + '\n'
        s += "R = " + str(self.rs) + '\n'
        s += "T = " + str(self.T) + '\n'
        s += "u0 = " + str(self.u0) + '\n'
        s += "uf = " + str(self.uf) + '\n'
        
        s += "C_avg = " + str(self.cs_avg) + '\n'
        s += "R_avg = " + str(self.rs_avg) + '\n'
        s += "T_avg= " + str(self.T_avg) + '\n'
        s += "u0_avg = " + str(self.u0_avg) + '\n'
        s += "uf_avg= " + str(self.uf_avg) + '\n'
        s += "sigma_rs " + str(self.sigma_rs/1e3) + '\n'
        s += "sigma_cs= " + str(self.sigma_cs*1e12) + '\n'
        s += "sigma_T= " + str(self.sigma_T*1e9) + '\n'
     
        return s
    
    def print(self):
        s=self.toString()
        print (s)
    
    def reset(self,ai0,aif):
        self.u0 = ai0 * self.i2u
        self.uf = aif * self.i2u

        self.calc_cs()
        
        self.rs_avg=self.rs
        self.cs_avg=self.cs
        self.u0_avg=self.u0
        self.uf_avg=self.uf
        self.T_avg=self.T
        
        self.sigma_rs=0
        self.sigma_cs=0
        self.sigma_T=0
        
        
    def publishMQTT(self):
        publish.single(self.name +"/u0",self.u0, hostname="localhost")
        publish.single(self.name +"/uf",self.uf, hostname="localhost")
        publish.single(self.name +"/u0_avg",self.u0_avg, hostname="localhost")
        publish.single(self.name +"/uf_avg",self.uf_avg, hostname="localhost")
        publish.single(self.name +"/R",self.rs_avg/1e3, hostname="localhost")
        publish.single(self.name +"/C",self.cs_avg*1e12, hostname="localhost")
        publish.single(self.name +"/T",self.T_avg*1e9, hostname="localhost")
   
        publish.single(self.name +"/sigma_R",self.sigma_rs/1e3, hostname="localhost")
        publish.single(self.name +"/sigma_C",self.sigma_cs*1e12, hostname="localhost")
        publish.single(self.name +"/sigma_T",self.sigma_T*1e9, hostname="localhost")
 



class Sensor():

    def __init__(self, name='aqs0', u=3.3, ai0=630, aif=440, dt=7 / 80e6):
        self.name=name
        self.ai0=ai0
        self.aif=aif
        self.cnt=0
        self.u = u
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
        
        self.calc_cs()
        
        self.k_avg=50.
        self.rs_avg=self.rs
        self.cs_avg=self.cs
        self.u0_avg=self.u0
        self.uf_avg=self.uf
        self.T_avg=self.T
        self.sigma_rs=0
        self.sigma_cs=0
        self.sigma_T=0

    def add(self,ai0,aif):
        self.ai0=ai0
        self.aif=aif
        self.cnt+=1
        self.u0 = ai0 * self.i2u
        self.uf = aif * self.i2u
        
        self.calc_cs()
        
        self.rs_avg=(self.rs_avg*(self.k_avg-1) + self.rs)/self.k_avg
        self.cs_avg=(self.cs_avg*(self.k_avg-1) + self.cs)/self.k_avg
        self.u0_avg=(self.u0_avg*(self.k_avg-1) + self.u0)/self.k_avg
        self.uf_avg=(self.uf_avg*(self.k_avg-1) + self.uf)/self.k_avg
        self.T_avg=(self.T_avg*(self.k_avg-1) + self.T)/self.k_avg
        
        d = sqrt((self.rs - self.rs_avg)**2)
        self.sigma_rs=(self.sigma_rs*(self.k_avg-1) + d)/self.k_avg
        d = sqrt((self.cs - self.cs_avg)**2)
        self.sigma_cs=(self.sigma_cs*(self.k_avg-1) + d)/self.k_avg
        d = sqrt((self.T - self.T_avg)**2)
        self.sigma_T=(self.sigma_T*(self.k_avg-1) + d)/self.k_avg
        
    def calc_cs(self):
    
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
        s = "name = " + self.name + '\n'
        s += "ai0 = " + str(self.ai0) + '\n'
        s += "aif = " + str(self.aif) + '\n'
        s += "C = " + str(self.cs) + '\n'
        s += "R = " + str(self.rs) + '\n'
        s += "T = " + str(self.T) + '\n'
        s += "u0 = " + str(self.u0) + '\n'
        s += "uf = " + str(self.uf) + '\n'
        
        s += "C_avg = " + str(self.cs_avg) + '\n'
        s += "R_avg = " + str(self.rs_avg) + '\n'
        s += "T_avg= " + str(self.T_avg) + '\n'
        s += "u0_avg = " + str(self.u0_avg) + '\n'
        s += "uf_avg= " + str(self.uf_avg) + '\n'
        s += "sigma_rs " + str(self.sigma_rs/1e3) + '\n'
        s += "sigma_cs= " + str(self.sigma_cs*1e12) + '\n'
        s += "sigma_T= " + str(self.sigma_T*1e9) + '\n'
     
        return s
    
    def print(self):
        s=self.toString()
        print (s)
    
    def reset(self,ai0,aif):
        self.u0 = ai0 * self.i2u
        self.uf = aif * self.i2u

        self.calc_cs()
        
        self.rs_avg=self.rs
        self.cs_avg=self.cs
        self.u0_avg=self.u0
        self.uf_avg=self.uf
        self.T_avg=self.T
        
        self.sigma_rs=0
        self.sigma_cs=0
        self.sigma_T=0
        
        
    def publishMQTT(self):
        publish.single(self.name +"/u0",self.u0, hostname="localhost")
        publish.single(self.name +"/uf",self.uf, hostname="localhost")
        publish.single(self.name +"/u0_avg",self.u0_avg, hostname="localhost")
        publish.single(self.name +"/uf_avg",self.uf_avg, hostname="localhost")
        publish.single(self.name +"/R",self.rs_avg/1e3, hostname="localhost")
        publish.single(self.name +"/C",self.cs_avg*1e12, hostname="localhost")
        publish.single(self.name +"/T",self.T_avg*1e9, hostname="localhost")
   
        publish.single(self.name +"/sigma_R",self.sigma_rs/1e3, hostname="localhost")
        publish.single(self.name +"/sigma_C",self.sigma_cs*1e12, hostname="localhost")
        publish.single(self.name +"/sigma_T",self.sigma_T*1e9, hostname="localhost")
        

# mhpc4-ubu
user = 'oh.marek.QYfJFA2xdKN4USYZ5HyXhF31p4Z7TZySNHfr4bby89A1PBNi5GL9AfLgxkQhMnnSDLfOMSHnk7O5Hug7Q'
url = "http://mhpc4-ubu:58080/rest/items/"


UDP_IP = ''
UDP_PORT = 61806

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

sock.settimeout(10 * 60.)

# cnt=0
# sensor0= Sensor()
# sensor1= Sensor()
# sensors = {'sensor0':sensor0,'sensor1':sensor1,  }
sensors = {}
for s in params:
    Sensor('aqs0')
# 'aqs0':,
#            'aqs1':Sensor('aqs1'),  
#            'aqs2':Sensor('aqs2'),  
#            'aqs3':Sensor('aqs3'),  
#            'aqs4':Sensor('aqs4'),  
#            }

while True:
    try:
        print(datetime.datetime.now(), "listening...")
        data, addr = sock.recvfrom(256)

        print (datetime.datetime.now(), "received message:", data, addr)
        splt = data.decode()
        d= splt.split(',')

        name=d[0]
        ai0=int(d[1])
        aif=int(d[2])
        # if name=='aqs0': continue
        
        sensor=sensors[name]
        if sensor.cnt==0: 
            sensor.reset(ai0,aif)   # only at begin some help on avarages
            sensor.cnt+=1
        else:
            sensor.add(ai0,aif)
        
        sensor.publishMQTT()
        sensor.print()
                
    except Exception as e:
        print (e)

if __name__ == '__main__':
    pass
