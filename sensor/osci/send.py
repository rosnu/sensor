import socket
import time

# UDP_IP = "127.0.0.1"  # Replace with the receiver's IP
UDP_IP = "192.168.4.1"  # Replace with the receiver's IP
UDP_PORT = 51807      # Replace with the receiver's port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(1000):
    print(i)
    value = str(i * 0.1)  # Send a series of values
    sock.sendto(value.encode(), (UDP_IP, UDP_PORT))
    time.sleep(0.2)  # Send data every 0.1 seconds