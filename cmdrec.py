import paho.mqtt.client as mqtt
import bluetooth
import threading
import time
import json

port = 1
topics = []
bd_addr = []
sockets = {}

login = "login"
password = "pass"

server = "localhost"

millis1 = []
millis2 = []

topicStatus = "MIPT-SportRoboticsClub/LunokhodFootball/Robots/Status/{0}"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("MIPT-SportRoboticsClub/LunokhodFootball/Internal/#")

    for i in range(num):
        client.subscribe(topics[i])
        millis1.append(1)
        millis2.append(1)


def on_message(client, userdata, msg):
    topic = str(msg.topic)
    rec = str(msg.payload)[2:-1]

    if "Internal" in topic:
        jsonMessage = json.loads(rec)
        if jsonMessage['command'] == "getConfig":
            playerId = topic.split("/")[-1]
            with open('gameConfiguration/config.json', 'r+', encoding='utf-8') as f:
                gameConfig = json.load(f)
            client.publish("MIPT-SportRoboticsClub/LunokhodFootball/Data/{0}".format(playerId), json.dumps(gameConfig))
    elif "Robots" in topic:
        print(rec)
        try:
            sockets[topic].send(rec + "\n")
        except:
            data_ = {"status" : "204"}
            client.publish(topic + "/status", json.dumps(data_))
            # client.publish(topicInternalData.format)


def connect():
    for i in range(num):
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        try:
            sock.connect((bd_addr[i], port))
            sock.setblocking(False)
            data_ = {"status" : "200"}
            client.publish(topics[i] + "/status", json.dumps(data_))
        except:
            data_ = {"status" : "204"}
            client.publish(topics[i] + "/status", json.dumps(data_))
        sockets[topics[i]] = sock
    print("connection done")


def bl_reconnect():
    while True:
        for i in range(num):
            try:
                sockets[topics[i]].getpeername()
            except:
                data_ = {"status" : "203"}
                client.publish(topics[i] + "/status", json.dumps(data_))
                try:
                    sockets[topics[i]].close()
                    sockets[topics[i]] = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                    sockets[topics[i]].connect((bd_addr[i], 1))
                    print("Connected")
                    data_ = {"status" : "200"}
                    client.publish(topics[i] + "/status", json.dumps(data_))
                except Exception as e:
                    print(e)
                    data_ = {"status" : "202"}
                    client.publish(topics[i] + "/status", json.dumps(data_))
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
                data_ = {"status" : "204"}
                client.publish(topics[i] + "/status", json.dumps(data_))
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
                    data_ = {"status" : "201"}
                    client.publish(topics[i] + "/status", json.dumps(data_))
            except:
                pass


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(login, password=password)
client.connect(server, 1883, 60)

with open('gameConfiguration/config.json', 'r+', encoding='utf-8') as f:
    gameConfig = json.load(f)

num = 0

for command in gameConfig['commands']:

    for player in gameConfig['commands'][command]:
        print("Player:", player)
        num += 1
        topics.append(player['topic'])
        bd_addr.append(player['mac'])


connectThread = threading.Thread(target=connect, args=(), daemon=True)
connectThread.start()

reconnThread = threading.Thread(target=bl_reconnect, args=(), daemon=True)
reconnThread.start()

heartbitThread = threading.Thread(target=hb, args=(), daemon=True)
heartbitThread.start()

heartbitThread2 = threading.Thread(target=hb_rec, args=(), daemon=True)
heartbitThread2.start()

client.loop_forever()
