'''
	Script to monitor a sensor and save MQTT messages, then upload to OPC-UA server.
	Author: Jonathan Lake
	Date: 01/03/2022
'''

'''
	CAPSTONE PROJECT PIPELINE (simple):
	RASPBERRY PI sensor information (hex) -> TEKTELIC GATEWAY (base64) -> HiveMQ Broker (base 64)
	|-> THIS script (base64 to hex conversion) -> HiveMQ (hex) and OPC-UA (hex)
'''

# python imports
from socket import timeout
import paho.mqtt.client as mqtt
import code
from opcua import Client
from opcua import ua
import time
import json
import sys
import base64

# function for decoding base64 encoded messages
def decodePhyPayload(msg):
	# extract the physical payload from the message
	# and convert to hex
	PHYPayload = base64.b64decode(msg).hex()

	return PHYPayload


# must be unique to other instances of this script that are running simulataneously
client_name = "loraNode"
# HiveMQ broker address
broker = "broker.hivemq.com"
# push topic from Tektelic gateway
topic = "v2/pushJonnyCapstone"

# create empty array for messages
msg_list = []

# mqtt 'on connect' behavior function
def on_connect(mqttc, obj, flags, rc):
	if rc == 0:
		mqttc.connected_flag = True
		print("connected ok")
	else:
		print("bad connection. returned code = ", rc)

# mqtt 'on subscribe' behavior function
def on_subscribe(mqttc, obj, mid, granted_qos):
	mqttc.subscribed_flag = True
	print("subscribed ok")

# mqtt 'on message' behavior function
def on_message(mqttc, obj, msg):
	global msg_list
	print(1)
	msg_py = json.loads(msg.payload)
	msg_py["topic"] = msg.topic
	msg_py["qos"] = msg.qos
	print(json.dumps(msg_py, sort_keys=True, indent=4, separators=(',', ': ')))
	msg_list += [msg_py]


if __name__ == '__main__':

	# configure mqtt
	mqtt.Client.connected_flag = False
	mqtt.Client.subscribed_flag = False
	mqttc = mqtt.Client(client_name)
	# bind call back functions
	mqttc.on_connect = on_connect
	mqttc.on_subscribe = on_subscribe
	mqttc.on_message = on_message
	# set username and password
	mqttc.username_pw_set('', password='')

	# connect to broker
	print("connecting to broker " + broker)
	try:
		mqttc.connect(broker, 1883, 60)  # connect to broker
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
				try:
					# get lora payload from msg
					RawPayload = msg_list[0]['0004A30B001A820C'][0]['values']['nsRawPayload']

				except KeyError:
					# handle exception
					print("Key not found.")

				# decode payload
				DecodedPayload = decodePhyPayload(RawPayload)
				# print decoded payload
				print("Decoded Payload: ", DecodedPayload)
				# publish decoded payload to HiveMQ broker
				mqttc.publish("v1/pull", DecodedPayload, 0, True)
                # remove the processed message
				msg_list = msg_list[1:]

				# set OPC-ua client address
				client = Client("opc.tcp://192.168.0.1:4840/")
				try:
					# connect to client
					print("connecting to OPC-UA client...")
					client.connect()
					print("connected ok")
					
					# get node value
					PLCstate_node = client.get_node('ns=3;s="OPC"."PLCstate"')
					PLCstate = PLCstate_node.get_value()
                    
					# set node value
					var1_setValue = ua.DataValue(ua.Variant(int(DecodedPayload,16), PLCstate_node.get_data_type_as_variant_type()))
					PLCstate_node.set_value(var1_setValue)

					# print new value
					print("Posted Value: ", int(DecodedPayload,16))
				
				except timeout:
					print("connection timed out")

				finally:
					# disconnect from client
					try:
						client.disconnect()
						print("disconnected ok")
					except AttributeError:
						print("OPC-UA client not connected")


	except KeyboardInterrupt: # Ctrl-c to quit
		print("stopping client loop") 
		mqttc.loop_stop()
		print("disconnecting from broker " + broker)
		mqttc.disconnect()