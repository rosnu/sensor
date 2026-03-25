import socket
import datetime

import matplotlib.pyplot as plt
from collections import deque
import time

import mhLib.Avg
from mhLib.Avg import  Avg

from  interpolated import Interpolator

aif_avg = Avg(20)
ai1_avg = Avg(20)

import aqsRC.interpolated
from  aqsRC.interpolated import Interpolator, data_aqs7
# aqs7_int=Interpolator(data_aqs7)


class LiveLinePlot:
    def __init__(self, max_len=200):
        self.max_len = max_len
        self.xdata = deque(maxlen=max_len)
        self.ydata = deque(maxlen=max_len)
        self.x2 = deque(maxlen=max_len)
        self.y2 = deque(maxlen=max_len)

        # Plot vorbereiten
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(3.5,5))
        self.line, = self.ax.plot([], [], linewidth=2)
        self.line2, = self.ax.plot([], [], label="Linie 2", linewidth=2)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        
        self.ax.set_xlim(0, 210)
        # self.ax.set_xscale('log')
        self.ax.set_ylim(900, 1700)

    def add_point(self, x, y,x2,y2):
        """Neuen Punkt hinzufügen und Plot aktualisieren."""
        self.xdata.append(x)
        self.ydata.append(y)
        self.x2.append(x2)
        self.y2.append(y2)

        self.line.set_data(self.xdata, self.ydata)
        self.line2.set_data(self.x2, self.y2)
        self.ax.relim()
        self.ax.autoscale_view()

        plt.pause(0.005)  # kleines Update-Intervall




UDP_IP = ''   
UDP_PORT = 61806  

BUFFER_SIZE = 1024 

plot = LiveLinePlot(max_len=200)
time.sleep(1)

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print(f"[*] UDP-Empfänger gestartet auf {UDP_IP}:{UDP_PORT}")
    print("[*] Warte auf Nachrichten...")
    
    cnt=0
    while True:
        cnt+=1
        if (cnt>200):
            plot.add_point(cnt, 0, cnt, 0)
            cnt=0
            plot.add_point(0, 0, 0, 0)

        data, addr = sock.recvfrom(BUFFER_SIZE) 
        message = data.decode('utf-8')
        
        
        print(f"\n[+] Nachricht empfangen von {addr}:")
        print(f"    Inhalt: '{message}'")
        
        d= message.split(',')
        
        print(d)
        if d[0]=='aqs7':
            # aif=int(d[1])/int(d[4])
            # ai1=int(d[2])/int(d[4])
            aif=int(d[1])
            ai1=int(d[2])

            # plot.add_point(int(d[3])/1e6, int(d[1])/10, int(d[3])/1e6, int(d[2])/10)

            aif_avg.add(aif)
            ai1_avg.add(ai1)

            R,C = aqs7_int.getRC (aif_avg.avg, ai1_avg.avg)
            print("R  ", round(R,1), ", C ", round(C*1e12,0))
            plot.add_point(cnt, aif_avg.avg, cnt, ai1_avg.avg)

            print(round(aif_avg.avg, 1),',', round(ai1_avg.avg,1))

        if d[0]=='aqs6':
            # aif=int(d[1])/int(d[4])
            # ai1=int(d[2])/int(d[4])
            # aif=int(d[1])/int(d[5])
            # ai1=int(d[2])/int(d[5])
            aif=int(d[1])
            ai1=int(d[2])

            # plot.add_point(int(d[3])/1e6, int(d[1])/10, int(d[3])/1e6, int(d[2])/10)
    
            aif_avg.add(aif)
            ai1_avg.add(ai1)
            # plot.add_point(cnt, aif_avg.avg, cnt, ai1_avg.avg)
            # plot.add_point(cnt, aif_avg.avg, cnt, ai1_avg.avg)
            plot.add_point(cnt, aif, cnt, ai1)
            plot.add_point(cnt, aif, cnt, ai1)
    
            print(round(aif_avg.avg, 1),',', round(ai1_avg.avg,1))
            
        if d[0]=='aqs5':
            aif=int(d[1]) #/int(d[4])
            ai1=int(d[2]) #/int(d[4])
            # plot.add_point(int(d[3])/1e6, int(d[1])/10, int(d[3])/1e6, int(d[2])/10)
    
            aif_avg.add(aif)
            ai1_avg.add(ai1)
            plot.add_point(cnt, aif_avg.avg, cnt, ai1_avg.avg)
    
            print(round(aif_avg.avg, 1),',', round(ai1_avg.avg,1))

except Exception as e:
    print(f"\n[!] Ein Fehler ist aufgetreten: {e}")
       
# # --- Beispiel: Nutzung ---
# if __name__ == "__main__":
#     import time, math
#
#     plot = LiveLinePlot(max_len=50)
#
#     for i in range(200):
#         plot.add_point(i, math.sin(i * 0.1))
#         time.sleep(0.02)
        
        
        