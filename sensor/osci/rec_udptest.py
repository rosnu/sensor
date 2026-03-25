import socket
import threading
import queue
import matplotlib.pyplot as plt
import struct
import numpy as np
import time

# UDP configuration
UDP_IP = "0.0.0.0"
UDP_PORT = 51807

# Function to receive UDP data
adc_mV = 4.096 / 32767.0;
adc_mV = 3.3 / 1024;

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
def udp_receiver():
    print(f"Listening for UDP data on {UDP_IP}:{UDP_PORT}...")

    while True:
        data, addr = sock.recvfrom(4096)  # Buffer size 
        # values = struct.unpack(f"{len(data)//2}h", data)
        # valuesV=np.array(values)*adc_mV
        # print(f"Empfangen von {addr}: {values}, {valuesV}")
        cnt = value = int.from_bytes(data[2048:2050], byteorder='little')
        print(cnt)
        # data_queue.put(valuesV)
        # time.sleep(1.)
        # try:
        #     value = float(data.decode().strip())
        #     print(f"Received: {value}")
        #     data_queue.put(value)  # Put data into the queue
        # except ValueError:
        #     print("Received invalid data")

# # Start the UDP receiver in a separate thread
# thread = threading.Thread(target=udp_receiver)
# thread.daemon = False
# thread.start()

while True:
    udp_receiver()


