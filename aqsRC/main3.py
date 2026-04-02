
import socket
import datetime
import json
from math import exp,log,sqrt
import numpy as np
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

from scipy.interpolate import SmoothBivariateSpline
from scipy.interpolate import interp1d


import sys
sys.path.append('/home/marek/docker/python/aqs')

from sensor_data import sensors #, aqs5, aqs6

mqtt_host = "192.168.178.40"

class Avg():
    def __init__(self, m_max=1e10): # equal waighted till..
        self.m_max=m_max
        self.m=0
        self.val=0
        self.diff=0
        
    def add(self, val=0):  # 
        
        if self.m<self.m_max: self.m+=1
        self.diff=val -self.val
        self.val+=self.diff/self.m
        
class Sensor():

    def __init__(self, name='aqs5'):
        self.name=name
        self.aqs=sensors[name] #sensor_data

        self.data = np.array(self.aqs['cal']) #calibration data
    
        self.measures = self.data[:, 2:]
        self.ufs=self.data[:, 2]
        self.u1s=self.data[:, 3]
        self.Rs = self.data[:, 0]
        self.Cs = self.data[:, 1]
        # self.Ts = self.data[:, 0] * self.data[:, 1]
        # self.usf_errs = np.zeros(len(self.data))
        # self.us1_errs = np.zeros(len(self.data))

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
                
        self.rs_interpol=self.get_rs_interpol()       
        self.fkt_rs_interpol = interp1d(self.rs_interpol[:,1],self.rs_interpol[:,0], kind='linear', fill_value='extrapolate')
        # rs=self.fkt_rs_interpol(u)
                
        self.m_avg=5.

        self.cnt=0
        self.cycle=0
        self.dcycle=0
       
        self.uf = 0
        self.u1 = 0
        self.u0 = 3.3
        self.ai_range = self.u0/self.aqs['params']['du']
        
        self.rs=0
        self.T=0
        self.Ts=0
        self.cs=0
               
        self.rs_avg=Avg(self.m_avg)
        self.cs_avg=Avg(self.m_avg)
        self.uf_avg=Avg(self.m_avg)
        self.u1_avg=Avg(self.m_avg)
        self.u0_avg=Avg(self.m_avg)
        self.T_avg=Avg(self.m_avg)
        self.Ts_avg=Avg(self.m_avg)
        # self.sigma_rs=0
        # self.sigma_cs=0
        # self.sigma_T=0
        self.status=1 # base, ok
        
    def get_rs_interpol(self): # exaggerate, puristic, sledgehammer to crack a nut
        # data must be rs sorted 
        ai_avg= Avg() # do avg for every calibration rs at dif. cs
        rs_ipol=[]
        r=0
        for d in self.data:
            if r!=d[0]:
                r=d[0]
                rs_ipol.append([d[0],0])
                ai_avg.m=0 #reset avg
            ai_avg.add(d[3])
            rs_ipol[-1][1]=ai_avg.val
            
        return np.array(rs_ipol)

    def add(self, aif, ai1, ai0):
        # self.cnt+=1
        
        # adjust if battery low
        self.aif=aif*self.ai_range/ai0
        self.ai1=ai1*self.ai_range/ai0
        self.ai0=ai0
        
        self.uf=aif*self.aqs['params']['du']
        self.u1=ai1*self.aqs['params']['du']
        self.u0=ai0*self.aqs['params']['du']
        
        self.uf_avg.add(self.uf)
        self.u1_avg.add(self.u1)
        self.u0_avg.add(self.u0)
        
        if  abs(self.uf_avg.diff)/self.uf_avg.val >=.2 or \
            abs(self.u1_avg.diff)/self.u1_avg.val >=.2 or \
            abs(self.u0_avg.diff)/self.u0_avg.val >=.2:
            self.status=0
            return 
        # k = 3.3/self.u0
        # k=3.3/(ai0*self.aqs['params']['du'])
        #
        # self.uf=3.3 * aif/ai0
        # self.u1=3.3 * ai1/ai0
        
        self.rs = self.spline_rs(self.aif,self.ai1)[0][0]
        self.rs2 = self.fkt_rs_interpol(self.ai1).item()
        self.cs = self.spline_cs(self.aif,self.ai1)[0][0]
      
        self.T= self.rs * self.cs
        self.Ts= self.rs*self.r0*1e-3/(self.rs+self.r0*1e-3) * self.cs
        
        self.rs_avg.add(self.rs)
        self.cs_avg.add(self.cs)
        # self.uf_avg.add(self.uf)
        # self.u1_avg.add(self.u1)
        # self.u0_avg.add(self.u0)
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
        s += "R2 = " + str(self.rs2) + '\n'
        s += "T = " + str(self.T) + '\n'
        s += "Ts = " + str(self.Ts) + '\n'
        s += "uf = " + str(self.uf) + '\n'
        s += "u1 = " + str(self.u1) + '\n'
        s += "u0 = " + str(self.u0) + '\n'
        
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
            "aif": round(self.aif,1),
            "ai1": round(self.ai1,1),
            "ai0": self.ai0,
            "uf" : round(self.uf,3),
            "uf_avg" : round(self.uf_avg.val,3),
            "u1" : round(self.u1,3),
            "u1_avg" : round(self.u1_avg.val,3),
            "u0" : round(self.u0,3),

            "R" : round(self.rs,3),
            "R_avg" : round(self.rs_avg.val,3),
            "R2" : round(self.rs2,3),
            "C" : round(self.cs,1),
            "C_avg" : round(self.cs_avg.val,1),
            "T" : round(self.T,1),
            "T_avg" : round(self.T_avg.val,1),
            "Ts" : round(self.Ts,1),
            "Ts_avg" : round(self.Ts_avg.val,1),
            "cnt" : self.cnt,
            "status" : self.status, # just a flag for ok/ko in db query
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
        
        # self.sigma_rs=0
        # self.sigma_cs=0
        # self.sigma_T=0
        
UDP_IP = ''
UDP_PORT = 61806

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

sock.settimeout(15 * 60.)

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)
client.reconnect_delay_set(min_delay=1, max_delay=60)
client.connect(mqtt_host, 1883, keepalive=60)
client.loop_start()

aqss = {
    'aqs1':Sensor(name='aqs1'),
    'aqs5':Sensor(name='aqs5'),
    'aqs6':Sensor(name='aqs6'),
    'aqs8':Sensor(name='aqs8'),
    }

def run():
    while True:
        try:
            print(datetime.datetime.now(), "listening...")
            data, addr = sock.recvfrom(256)
            
            print (datetime.datetime.now(), "received message:", data, addr)
            
            payload = data.decode()
            # print (payload)
            if payload[0]=="{": #json
                msg = json.loads(payload)
                name = msg["name"]
                # client.publish(name, payload, )
                # print (msg)
                sensor=aqss[name]
                aif=msg["aif"]
                ai1=msg["ai1"]
                ai0=msg["ai0"]
                sensor.add(aif, ai1, ai0)
                sensor.cnt=msg["cnt"]
                json_=sensor.toJson()
                client.publish(name, json_, )

                print(json_)
                pass
            else:  #list, depricated - see previous commit
                print ("msg error")
    
        except Exception as e:
            print (e)

if __name__ == '__main__':
    run()  
    pass
