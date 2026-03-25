import socket
import threading
import queue
import matplotlib.pyplot as plt
import struct
import numpy as np
import time
import db


# UDP configuration
UDP_IP = "0.0.0.0"  # Replace with the IP address of the sender
UDP_PORT = 51807  # Replace with the port number

BUFFER_SIZE = 65536

osc_db=db.OscDb()

datastore=[]
def udp_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP data on {UDP_IP}:{UDP_PORT}...")
    cnt=0
    while True:
        cnt+=1
        print(cnt)
        bufsize = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        print(bufsize)
        t0=time.time()
        data, addr = sock.recvfrom(2048+20)
        t1=time.time()
        datastore.append(data)
        t2=time.time()
        
        print(t1-t0,t2-t1 )
        if cnt > 200: return
        # osc_db.insert_array(data)
        # data1=data[:2048]
        # info=data[2048:]
        # data1 = struct.unpack(f"{len(data)//2}h", data)
        # valuesV = np.array(data1[:1024]) * adc_mV
        # info=data1[1024:]
        # print(f"Empfangen von {addr}: {values}, {valuesV}")
        # valuesV[0]=values[0]
        # print(valuesV[:10])
        # print(int(info[0]), int(info[1]), int(info[2]))
        # data_queue.put(valuesV)
        # print('qsize ', data_queue.qsize())
        # time.sleep(.1)
        # try:
        #     value = float(data.decode().strip())
        #     print(f"Received: {value}")
        #     data_queue.put(value)  # Put data into the queue
        # except ValueError:
        #     print("Received invalid data")

def save():
    for a in datastore:
        osc_db.insert_array(a)

udp_receiver()
save()

# Start the UDP receiver in a separate thread
# thread = threading.Thread(target=udp_receiver)
# thread.daemon = True
# thread.start()
#
# # Update the plot in the main thread
# update_plot()
