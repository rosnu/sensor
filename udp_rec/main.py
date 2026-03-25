import socket
import datetime

UDP_IP = ''
UDP_PORT = 61806

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

sock.settimeout(10 * 60.)

cnt=0

def init_sensors():
    pass
    


while True:
    cnt+=1
    try:
        print(datetime.datetime.now(), "listening...")
        data, addr = sock.recvfrom(256)
        print (datetime.datetime.now(), "received message:", data, addr)

        splt = data.decode()
        d= splt.split(',')

        if d[0].startswith('aqs'):
            if d[0]=='aqs5':
                
            

        ai0=int(d[0])
        aif=int(d[1])
         
    except Exception as e:
        print (e)

if __name__ == '__main__':
    pass







