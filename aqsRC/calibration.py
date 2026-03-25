import socket
import threading
import sys
import os
import json
import csv
import paho.mqtt.client as mqtt

import mhLib.Avg
from mhLib.Avg import  Avg

aif_avg = Avg(20)
ai1_avg = Avg(20)
cnt=0

rs = [2.2, 4.4, 9.1, 13.8, 23.8, 10e6]
cs=[0, 47, 100, 147, 200, 247]


def append_row_to_csv(file_path, row_data):
    """
    Appends a row (list or tuple) to a CSV file.

    :param file_path: Path to the CSV file
    :param row_data: List or tuple representing the row to append
    """
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(row_data)


def append_list_to_json_file(file_path, data_list):
    # Ensure data_list is a list
    if not isinstance(data_list, list):
        raise ValueError("data_list must be a list")

    # Load existing data if file exists and is not empty
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
            if not isinstance(existing, list):
                raise ValueError("JSON file does not contain a list")
    else:
        existing = []

    # Append new items
    # existing.extend(data_list)
    existing.append(data_list)

    # Write updated list back to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)







def proc_data(data):
    global cnt
    cnt+=1
    message = data.decode('utf-8')
        
        
    # print(f"\n[+] Nachricht empfangen von {addr}:")
    # print(f"    Inhalt: '{message}'")
        
    d= message.split(',')
    # print(d)
    if d[0]=='aqs5':
        aif_avg.add(int(d[1]))
        ai1_avg.add(int(d[2]))
        
        aif=round(aif_avg.avg,1)
        ai1=round(ai1_avg.avg,1)
        print (d[1], ", " ,d[2], ", ", cnt )
        print (aif, ", " ,ai1)
        print()

def receive_udp(sock):
    """Hauptempfangsschleife für UDP-Nachrichten - BLOCKIEREND"""
    while True:
        try:
            # Blockierendes recvfrom - kein Timeout!
            data, addr = sock.recvfrom(1024)
            if data:
                # print(f"\n[UDP von {addr}]: {data.decode()}")
                proc_data(data)
                # print("> ", end="", flush=True)
        except Exception as e:
            print(f"\nEmpfangsfehler: {e}")
            break
            raise

def get_user_input(running_event):
    global cnt
    c_idx=0
    r_idx=0
    while running_event.is_set():
        try:
            user_input = input("> ")
            if user_input.lower() == "r": #reset
            # if user_input == "R": #reset
                aif_avg.avgConst=0
                ai1_avg.avgConst=0
                cnt=0
                c_idx=0
                r_idx=0
            user_input = input("> ")
            if user_input.lower() == "s": #reset
                mes=[round(aif_avg.avg,1), round( ai1_avg.avg,1)]
                append_list_to_json_file("mes.json", mes)
                append_row_to_csv("mes.txt", mes)
                print(mes)

            if user_input.lower() == "quit":
                print("Beende Programm...")
                running_event.clear()
                os._exit(0)
            print(f"Eingabe verarbeitet: {user_input}")
        except EOFError:
            break

def main():
    # UDP Socket setup - KEIN TIMEOUT
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('0.0.0.0', 61806))
    # KEIN settimeout() hier!
    
    print("UDP-Empfänger gestartet. Port: x")
    print("Tippe 'quit' zum Beenden")
    print("> ", end="", flush=True)
    
    # Event zur Steuerung der Threads
    running = threading.Event()
    running.set()
    
    # Threads starten
    receive_thread = threading.Thread(target=receive_udp, args=(udp_socket,), daemon=True)
    input_thread = threading.Thread(target=get_user_input, args=(running,), daemon=True)
    
    receive_thread.start()
    input_thread.start()
    
    # Hauptthread wartet auf Beendigung
    try:
        while running.is_set():
            # Kurz warten, um CPU-Last zu reduzieren
            receive_thread.join(0.1)
            input_thread.join(0.1)
    except KeyboardInterrupt:
        print("\nProgramm durch Strg+C beendet.")
    finally:
        running.clear()
        udp_socket.close()


def watch():
    
    
    pass

def main2():
    client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    client.reconnect_delay_set(min_delay=1, max_delay=60)
    client.connect("192.168.178.40", 1883, keepalive=60)
    client.loop_start()
    

    pass



if __name__ == "__main__":
    main()