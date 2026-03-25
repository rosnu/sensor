import socket
import struct
import numpy as np

UDP_IP = "0.0.0.0"  # Lausche auf allen Interfaces
UDP_PORT = 51807
BUFFER_SIZE = 8192 #4096  # Muss groß genug sein für dein Array

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# print(f"Empfange UDP-Daten auf Port {UDP_PORT}...")

# //  GAIN_TWOTHIRDS: +/- 6.144V
# //  GAIN_ONE: +/- 4.096V (default)
# //  GAIN_TWO: +/- 2.048V
# //  GAIN_FOUR: +/- 1.024V
# //  GAIN_EIGHT: +/- 0.512V
# //  GAIN_SIXTEEN: +/- 0.256V

adc_mV = 4.096 / 32767.0;







while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    # print (data, len(data))
    # values = struct.unpack(f">{len(data)//4}i", data)  # Entpacken der Integer-Werte
    # values = struct.unpack(f"{len(data)//4}i", data)  # Entpacken der Integer-Werte
    # values = struct.unpack(f"<{len(data)//2}h", data)  # '<h' = Little Endian int16_t
    values = struct.unpack(f"{len(data)//2}h", data)
    valuesV=np.array(values)*adc_mV
    # print(f"Empfangen von {addr}: {values}, {valuesV}")
    print(valuesV[0], valuesV[1])
