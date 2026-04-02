import paho.mqtt.client as mqtt
from mhLib.Avg import Avg
import json

BROKER = "192.168.178.40"      # or IP / hostname
PORT = 1883
aqs='aqs6'

aif_avg=Avg(100)
ai1_avg=Avg(100)
uf_avg=Avg(100)
u1_avg=Avg(100)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
        # client.subscribe([
        #             (aqs+"/aif", 0), #topic, QoS
        #             (aqs+"/ai1", 0),
        #             ])
        client.subscribe(aqs)
    else:
        print("Connect failed, rc=", rc)

aif=0
ai1=0
def on_message(client, userdata, msg):

    # payload = data.decode()
    # print (payload)
    # if payload[0]=="{": #json
    data = json.loads(msg.payload)
    # name = data["name"]
    aif=data["aif"]
    ai1=data["ai1"]
    ai0=data["ai0"]
    uf=data["uf"]
    u1=data["u1"]
    u0=data["u0"]

    uf_avg.add(uf)
    u1_avg.add(u1)
        
    # print (msg.payload.decode())
    # # return
    # global aif,ai1
    # if msg.topic==aqs+'/aif':
    #     aif=int(msg.payload.decode())
    #     aif_avg.add(aif)
    #     # avg=aif_avg.avg
    # if msg.topic==aqs+'/ai1':
    #     ai1=int(msg.payload.decode())
    #     ai1_avg.add(ai1)
    # print(f"{msg.topic}: {msg.payload.decode()}, avg  {round(avg,1)}, cnt {aif_avg.avgConst}")
    print(f"{round(uf_avg.avg,3)},  {round(u1_avg.avg,3)}, {uf_avg.avgConst}")
    # print(f"{aif}, {ai1}, ")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, keepalive=60)
client.loop_forever()
