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

mqtt_host = "192.168.178.40"

# ai_ref - U @sensor, measured without sensor (divider + diode), for calc Udiode
params = {
    # 'aqs0':{'u':3.3, 'ai_ref':929, 'ai0':630, 'aif':440, 'frq':2000, },  # 'frq' kHz, 
    # 'aqs1':{'u':3.3, 'ai_ref':929, 'ai0':630, 'aif':440, 'frq':2000, },  # 'frq' kHz, 
    # 'aqs2':{'u':3.3, 'ai_ref':929, 'ai0':630, 'aif':440, 'frq':2000, },  # 'frq' kHz, 
    # 'aqs3':{'u':3.3, 'ai_ref':929, 'ai0':630, 'aif':440, 'frq':2000, },  # 'frq' kHz, 
    # # 'aqs4':{'u':3.3, 'ai_ref':970, 'ai0':630, 'aif':440, 'frq':2000, },  # 'frq' kHz, 
    # 'aqs4':{'u':3.3, 'ai_ref':960, 'ai0':630, 'aif':440, 'frq':2000, },  # 'frq' kHz, 
    
    # 'aqs4':{'u':3.3, 'ai_u33':1024,'ai_ref':1000, 'ai0':500, 'aif':400, 'ai_r': 320, 'frq':10000, },  # 'frq' kHz, 
    'aqs6':{'type':'xiao32c6', 'u':3.3, 'ai_u33':3300,'ai_ref':3210, 'ai0':1574, 'aif':1186, 'ais0':3210, 'ai_r': 470, 'frq':1024*1024*2, },  
    # 'aqs7':{'u':3.3, 'ai_u33':3300,'ai_ref':3265, 'ai0':1574, 'aif':1186, 'ai_r': 470, 'frq':10000, },  # 'frq' kHz, 
        }

class Sensor():

    def __init__(self, name='aqs0'):
        self.name=name
        self.params=params[name]
        
        self.ai_ref = self.params['ai_ref']
        self.ai0=self.params['ai0']
        self.aif=self.params['aif']
        self.ais0=self.params['ais0']
        self.u = self.params['u']
        self.ai_u33=self.params['ai_u33']
        
        self.r0 = 4.7e3
        self.k_avg=20.

        self.cnt=0
        self.ai2u = self.u  / self.ai_u33
       
        self.u0 = self.ai0 * self.ai2u
        self.uf = self.aif * self.ai2u
        self.us0 = self.ais0*self.ai2u
        self.rout = self.params['ai_r']*1e3
        # self.cout = 10e-9
        # self.ud = .06 #.26
        # self.dt = 1./(self.params['frq']*1000)/2.
        
        # to calculate
        self.us=0 #measure?
        self.rs=0
        self.T=0
        self.cs=0
        
        self.calc_ud()
        self.calc_cs()
        
        self.rs_avg=self.rs
        self.cs_avg=self.cs
        self.u0_avg=self.u0
        self.uf_avg=self.uf
        self.T_avg=self.T
        self.sigma_rs=0
        self.sigma_cs=0
        self.sigma_T=0

    def calc_ud(self):
        
        k=self.rout/(self.r0+self.rout) 
        aid = self.ai_u33*k - self.ai_ref
        self.ud = aid*self.ai2u
        
    def add(self,ai0,aif,ais0):
        self.ai0=ai0
        self.aif=aif
        self.ais0=ais0
        # self.cnt+=1
        self.u0 = ai0 * self.ai2u
        self.uf = aif * self.ai2u
        self.us0 = ais0*self.ai2u
        self.ud=self.us0-self.u0
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
        r= self.rs*self.r0/(self.rs+self.r0)
        self.cs = self.T /r
    
        pass
    def calc_T(self):
        '''
        yt = y0* exp(-t/T)
        log(yt)=log(y0)-t/T
        t/T = log(y0)-log(yt)
        T=t/(log(y0)-log(yt))
        '''
        # calulated for falling edge, symmetrie assumed
        # self.T = self.dt / (log(self.uf+self.ud) - log(self.u0-self.uf))
        u0=self.u0+self.ud
        uf=self.uf+self.ud
        # self.T = self.dt / (log(u0) - log(u0-uf))
        try:
            # self.T = self.dt / (log(uf) - log(u0-uf))  
            self.T = self.dt / log(uf/(u0-uf))  
        except:
            print(uf, u0-uf)
            print(self.aif, self.ai0)
            # print(e)
    
        print (uf, u0-uf)
    def calc_rs(self):
               
        i0 = (self.u - self.us0) / self.r0
        irout = self.u0 / self.rout 
        irs = i0 - irout
        self.rs = self.us0 / irs
    
    def toString(self):
        s = "\nname = " + self.name + '\n'
        s += "dt = " + str(self.dt*1e9) + '\n'
        s += "frq = " + str(1./(self.dt*2)*1e-3) + '\n'
        s += "ai0 = " + str(self.ai0) + '\n'
        s += "aif = " + str(self.aif) + '\n'
        s += "ais0 = " + str(self.ais0) + '\n'
        s += "ud  = " + str(self.ud) + '\n'
        s += "C = " + str(self.cs) + '\n'
        s += "R = " + str(self.rs) + '\n'
        s += "T = " + str(self.T) + '\n'
        s += "u0 = " + str(self.u0) + '\n'
        s += "uf = " + str(self.uf) + '\n'
        s += "us0 = " + str(self.us0) + '\n'
        
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
    
    def reset(self,ai0,aif, ai1):
        # # self.cnt +=1;
        # self.u0 = ai0 * self.ai2u
        # self.uf = aif * self.ai2u
        # self.us=ai1* self.ai2u
        # self.ud=self.us-self.u0
        # self.calc_cs()
        
        self.add(ai0,aif, ai1)
        
        self.rs_avg=self.rs
        self.cs_avg=self.cs
        self.u0_avg=self.u0
        self.uf_avg=self.uf
        self.T_avg=self.T
        
        self.sigma_rs=0
        self.sigma_cs=0
        self.sigma_T=0
        
        
    def publishMQTT(self):
        publish.single(self.name +"/u0",self.u0, hostname=mqtt_host)
        publish.single(self.name +"/uf",self.uf, hostname=mqtt_host)
        publish.single(self.name +"/u0_avg",self.u0_avg, hostname=mqtt_host)
        publish.single(self.name +"/uf_avg",self.uf_avg, hostname=mqtt_host)
        publish.single(self.name +"/R",self.rs/1e3, hostname=mqtt_host)
        publish.single(self.name +"/C",self.cs*1e12, hostname=mqtt_host)
        publish.single(self.name +"/Ravg",self.rs_avg/1e3, hostname=mqtt_host)
        publish.single(self.name +"/Cavg",self.cs_avg*1e12, hostname=mqtt_host)
        publish.single(self.name +"/T",self.T_avg*1e9, hostname=mqtt_host)
   
        publish.single(self.name +"/sigma_R",self.sigma_rs/1e3, hostname=mqtt_host)
        publish.single(self.name +"/sigma_C",self.sigma_cs*1e12, hostname=mqtt_host)
        publish.single(self.name +"/sigma_T",self.sigma_T*1e9, hostname=mqtt_host)
        

# mhpc4-ubu
user = 'oh.marek.QYfJFA2xdKN4USYZ5HyXhF31p4Z7TZySNHfr4bby89A1PBNi5GL9AfLgxkQhMnnSDLfOMSHnk7O5Hug7Q'
url = "http://mhpc4-ubu:58080/rest/items/"


UDP_IP = ''
UDP_PORT = 51806

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

sock.settimeout(10 * 60.)

# cnt=0
# sensor0= Sensor()
# sensor1= Sensor()
# sensors = {'sensor0':sensor0,'sensor1':sensor1,  }
sensors = {}
for k,v in params.items():
    sensors[k]=Sensor(name=k)
   
    pass

while True:
    try:
        print(datetime.datetime.now(), "listening...")
        data, addr = sock.recvfrom(256)

        print (datetime.datetime.now(), "received message:", data, addr)
        splt = data.decode()
        d= splt.split(',')

        name=d[0]
        aif=int(d[1])
        ai0=int(d[2])
        frq=int(d[3])
        ais0=int(d[4])
        
        # ai_u33=int(d[3])
        # if name=='aqs0': continue
        sensor=sensors[name]
        sensor.dt=1./frq/2. 
        if sensor.cnt==3: 
            sensor.reset(ai0,aif,ais0)   # only at begin some help on avarages
        else:
            sensor.add(ai0, aif, ais0)
            
        sensor.cnt+=1

        # print ('frq ', frq)
        # print ('ud ', sensor.ud)
        
        sensor.publishMQTT()
        sensor.print()
                
    except Exception as e:
        print (e)

if __name__ == '__main__':
    
    # s=Sensor('aqs7')
    # f=2e6
    # s.dt=1./frq/2.
    # ai0=1325
    # aif=1002
    # ais0=1644
    #
    # s.add(ai0, aif, ais0)
    # s.print()
    
    
    pass
