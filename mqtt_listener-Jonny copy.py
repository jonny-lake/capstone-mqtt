''' 
	Script to monitor a sensor and save MQTT messages.
	Author: Jonathan Lake
	Date: 01/03/2022
'''

import paho.mqtt.client as mqtt
import time
import sys
from lora.crypto import loramac_decrypt
import base64
	
def decodePhyPayload(msg, AppSKey, DevAddr):
	# extract the physical payload from the message
	# and convert to hex
	PHYPayload = msg
	PHYPayload = base64.b64decode(PHYPayload).hex()

	return PHYPayload

client_name = "loraNode" # must be unique to other instances of this script that are running simulataneously
broker = "broker.hivemq.com" 
topic = "v1/pull"
SIM_MODE = False

msg_list = []

def on_connect(mqttc, obj, flags, rc):
	if rc == 0:
		mqttc.connected_flag = True
		print("connected ok")
	else:
		print("bad connection. returned code = " , rc)

def on_subscribe(mqttc, obj, mid, granted_qos):
	mqttc.subscribed_flag = True
	print("subscribed ok")	

def on_message(mqttc, obj, msg):
	global msg_list
	print(1)
	msg_py = msg.payload
	msg_list += [msg_py]
	
if __name__ == '__main__':
	
	# configure mqtt
	mqtt.Client.connected_flag = False
	mqtt.Client.subscribed_flag = False
	mqttc = mqtt.Client(client_name)
	mqttc.on_connect = on_connect # bind the call back functions
	mqttc.on_subscribe = on_subscribe
	mqttc.on_message = on_message
	mqttc.username_pw_set('', password='')
	
	# connect to broker
	print("connecting to broker " + broker)
	try: 
		mqttc.connect(broker, 1883, 60) # connect to broker
	except:
		print("can't connect")
		sys.exit(1)
	mqttc.loop_start()
	while not mqttc.connected_flag:
		print("waiting for connection...")
		time.sleep(1)
	
	# subscribe to topic
	print("subscribing to topic " + topic)	
	mqttc.subscribe(topic, 1)
	while not mqttc.subscribed_flag:
		print("waiting to subscribe...")
		time.sleep(1)
	
	# loop forever!
	num_msgs = 0
	try:
		while True:
			time.sleep(1)
			while msg_list != []:
				print(msg_list[0])
				# remove the processed message
				msg_list = msg_list[1:]
				
	except KeyboardInterrupt: # Ctrl-c to quit
		print("stopping client loop") 
		mqttc.loop_stop()
		print("disconnecting from broker " + broker)
		mqttc.disconnect()