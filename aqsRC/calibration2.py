import paho.mqtt.client as mqtt
from mhLib.Avg import Avg

BROKER = "192.168.178.40"      # or IP / hostname
PORT = 1883

aif_avg=Avg(100)
ai1_avg=Avg(100)

aqs='aqs6'

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
        client.subscribe([
                    (aqs+"/aif", 0), #topic, QoS
                    (aqs+"/ai1", 0),
                    ])
        # client.subscribe("aqs6")
    else:
        print("Connect failed, rc=", rc)

aif=0
ai1=0
def on_message(client, userdata, msg):
    
    # print (msg.payload.decode())
    # return
    global aif,ai1
    if msg.topic==aqs+'/aif':
        aif=int(msg.payload.decode())
        aif_avg.add(aif)
        # avg=aif_avg.avg
    if msg.topic==aqs+'/ai1':
        ai1=int(msg.payload.decode())
        ai1_avg.add(ai1)
    # print(f"{msg.topic}: {msg.payload.decode()}, avg  {round(avg,1)}, cnt {aif_avg.avgConst}")
        print(f"{round(aif_avg.avg,1)},  {round(ai1_avg.avg,1)}, {aif_avg.avgConst}")
    print(f"{aif}, {ai1}, ")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, keepalive=60)
client.loop_forever()
