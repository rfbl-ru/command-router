import paho.mqtt.client as mqtt
import time
import threading

topic="topic"

login = "login"
password = "passwd"

server = "www.example.com"
millis1 = 0

def on_connect(client, userdata, flags, rc):
	client.subscribe(topic+"/status") # подписываемся на топик для получения статуса передачи данных 


def on_message(client, userdata, msg):
	rec = str(msg.payload)
	if rec[2:len(rec)-1] == "201":
		millis2 = int(round(time.time() * 1000)) 

def send():
	while True: 
		client.publish(topic, "w") # отправляем команду "command" на робот
		global millis1
		millis1 = int(round(time.time() * 1000))
		time.sleep(7)	

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(login, password=password)
client.connect(server, 1883, 60)

reconnThread = threading.Thread(target=send, args=(), daemon=True)
reconnThread.start()

client.loop_forever()



