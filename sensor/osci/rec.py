import socket
import matplotlib
# matplotlib.use('TkAgg')  # Use Tkinter backend
import matplotlib.pyplot as plt
import numpy as np
import threading
import struct

# UDP configuration
# UDP_IP = "127.0.0.1"  # Replace with the IP address of the sender
UDP_IP = "0.0.0.0"  # Replace with the IP address of the sender
UDP_PORT = 51807       # Replace with the port number

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
def update_plot(new_data):
    y_data =new_data
    x_data=np.arange(0, len(new_data))  # Use index as time
    line.set_xdata(x_data)
    line.set_ydata(y_data)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw()
    fig.canvas.flush_events()

def update_plot_bak(new_data):
    y_data.append(new_data)
    x_data.append(len(x_data))  # Use index as time
    line.set_xdata(x_data)
    line.set_ydata(y_data)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw()
    fig.canvas.flush_events()

adc_mV = 4.096 / 32767.0;
def udp_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP data on {UDP_IP}:{UDP_PORT}...")

    while True:
        data, addr = sock.recvfrom(2048)  # Buffer size is 1024 bytes
        values = struct.unpack(f"{len(data)//2}h", data)
        valuesV=np.array(values)*adc_mV
        # print(f"Empfangen von {addr}: {values}, {valuesV}")
        print(valuesV[0], valuesV[1])

        # try:
        #     value = float(data.decode().strip())
        #     print(f"Received: {value}")
        #     update_plot(value)
        # except ValueError:
        #     print("Received invalid data")

# Start the UDP receiver in a separate thread
thread = threading.Thread(target=udp_receiver)
# thread.daemon = True
thread.daemon = False
thread.start()

# Show the plot
plt.show()
