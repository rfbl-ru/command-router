import paho.mqtt.client as mqtt
import bluetooth
import threading
import time
import json

port = 1
topics = []
bd_addr = []
sockets = {}

login = "mqtt_login"
password = "mqtt_pwd"

server = "host"

millis1 = []
millis2 = []


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    for i in range(num):
        client.subscribe(topics[i])
        client.subscribe(topics[i] + '/server')
        client.subscribe(topics[i] + '/addMac')
        millis1.append(1)
        millis2.append(1)


def on_message(client, userdata, msg):
    tosend = str(msg.payload)
    tosend = tosend[2:len(tosend) - 1]
    topic = str(msg.topic)
    print(tosend)
    if topic.find('server') > -1 and tosend.find('cams') > -1:
        pld = ', '.join(map(str, cams))
        pld = pld.replace('\'', '"')
        client.publish(msg.topic, "[" + pld + "]")
    elif topic.find('addMac') > -1:
        pass
    elif topic.find('/') > -1:
        pass
    else:
        print(tosend)
        try:
            sockets[msg.topic].send(tosend + "\n")
        except:
            client.publish(msg.topic + "/status", "204")


def connect():
    for i in range(num):
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        try:
            sock.connect((bd_addr[i], port))
            sock.setblocking(False)
            client.publish(topics[i] + "/status", "200")
        except:
            client.publish(topics[i] + "/status", "202")
        sockets[topics[i]] = sock
    print("connection done")


def bl_reconnect():
    while True:
        for i in range(num):
            try:
                sockets[topics[i]].getpeername()
            except:
                client.publish(topics[i] + "/status", "203")
                try:
                    sockets[topics[i]].close()
                    sockets[topics[i]] = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                    sockets[topics[i]].connect((bd_addr[i], 1))
                    print("Connected")
                    client.publish(topics[i] + "/status", "200")
                except Exception as e:
                    print(e)
                    client.publish(topics[i] + "/status", "202")
                    print("Connection error")
        time.sleep(0.1)


def hb():
    while True:
        for i in range(num):
            try:
                sockets[topics[i]].send("p")
                millis1[i] = int(round(time.time() * 1000))
            except Exception as e:
                print(e)
                client.publish(topics[i] + "/status", "204")
        time.sleep(5)


def hb_rec():
    while True:
        for i in range(num):
            try:
                b = sockets[topics[i]].recv(1)
                msg = b.decode()
                print(msg)
                if msg == "o":
                    millis2[i] = int(round(time.time() * 1000))
                    print(millis2[i] - millis1[i])
                    client.publish(topics[i] + "/time", str(millis2[i] - millis1[i]))
                if msg == "l":
                    client.publish(topics[i] + "/status", "201")
            except:
                pass


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(login, password=password)
client.connect(server, 1883, 60)

with open('config.json', 'r', encoding='utf-8') as f:
    text = json.load(f)

with open('camsConfig.json', 'r', encoding='utf-8') as f:
    cams = json.load(f)

num = 0

for cmd in text['commands']:
    num += 1
    topics.append(cmd['topic'])
    bd_addr.append(cmd['mac'])
text = ""

connectThread = threading.Thread(target=connect, args=(), daemon=True)
connectThread.start()

reconnThread = threading.Thread(target=bl_reconnect, args=(), daemon=True)
reconnThread.start()

heartbitThread = threading.Thread(target=hb, args=(), daemon=True)
heartbitThread.start()

heartbitThread2 = threading.Thread(target=hb_rec, args=(), daemon=True)
heartbitThread2.start()

client.loop_forever()
