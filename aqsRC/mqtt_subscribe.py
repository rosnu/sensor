import paho.mqtt.client as mqtt
from mhLib.Avg import Avg

BROKER = "192.168.178.40"      # or IP / hostname
PORT = 1883
TOPIC = "aqs5/uf"

aif_avg=Avg(100)
ai1_avg=Avg(100)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
        client.subscribe([
                    ("aqs5/aif", 0),
                    ("aqs5/ai1", 1),
                    ])
        # client.subscribe(TOPIC)
    else:
        print("Connect failed, rc=", rc)

def on_message(client, userdata, msg):
    avg=0
    if msg.topic=='aqs5/aif':
        aif_avg.add(int(msg.payload.decode()))
        avg=aif_avg.avg
    if msg.topic=='aqs5/ai1':
        ai1_avg.add(int(msg.payload.decode()))
        avg=ai1_avg.avg
    print(f"{msg.topic}: {msg.payload.decode()}, avg  {round(avg,1)}, cnt {aif_avg.avgConst}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, keepalive=60)
client.loop_forever()
