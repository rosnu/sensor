import socket
import threading
import queue
import matplotlib.pyplot as plt
import struct
import numpy as np
import time

# UDP configuration
UDP_IP = "0.0.0.0"  # Replace with the IP address of the sender
UDP_PORT = 51807  # Replace with the port number

# Queue for thread-safe data sharing
data_queue = queue.Queue()

# Initialize the plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
x_data, y_data = [], []
line, = ax.plot(x_data, y_data)
ax.set_autoscaley_on(True)
ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.grid()


# Function to update the plot
def update_plot():
    while True:
        try:
            # Get data from the queue (non-blocking)
            # value = data_queue.get_nowait()
            # y_data.append(value)
            # x_data.append(len(x_data))  # Use index as time
            y_data = data_queue.get_nowait()
            # print(data_queue.qsize())
            x_data = np.arange(0, len(y_data))  # Use index as time
            line.set_xdata(x_data)
            line.set_ydata(y_data)
            ax.set_ylim(0, 5)
            ax.set_xlim(0, 1024)
            # ax.relim()
            # ax.autoscale_view()
            fig.canvas.draw()
            fig.canvas.flush_events()
        except queue.Empty:
            pass  # No data in the queue
        plt.pause(0.01) #01)  # Small pause to allow GUI updates


# Function to receive UDP data
# adc_mV = 4.096 / 32767.0
adc_mV = 3.3 / 1024 * (1.26 / 1.4)


def udp_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP data on {UDP_IP}:{UDP_PORT}...")
    cnt=0
    while True:
        cnt+=1
        print(cnt)
        data, addr = sock.recvfrom(2048+20)  # Buffer size 
        # data1=data[:2048]
        # info=data[2048:]
        data1 = struct.unpack(f"{len(data)//2}h", data)
        valuesV = np.array(data1[:1024]) * adc_mV
        info=data1[1024:]
        # print(f"Empfangen von {addr}: {values}, {valuesV}")
        # valuesV[0]=values[0]
        # print(valuesV[:10])
        print(int(info[0]), int(info[1]), int(info[2]))
        data_queue.put(valuesV)
        print('qsize ', data_queue.qsize())
        time.sleep(.1)
        # try:
        #     value = float(data.decode().strip())
        #     print(f"Received: {value}")
        #     data_queue.put(value)  # Put data into the queue
        # except ValueError:
        #     print("Received invalid data")


# Start the UDP receiver in a separate thread
thread = threading.Thread(target=udp_receiver)
thread.daemon = True
thread.start()

# Update the plot in the main thread
update_plot()
