# MQTT to OPC-UA Capstone Project
> The goal of this project is to create edge detection sensor nodes which can be added to control systems using lorawan technology and machine learning.

> My role has been to develop a bridge between a Raspberry PI (sensor), a Tektelic Gateway and Server, as well as a bridge between the server and a PLC.

> The sensor sends the state of the control (in hex) to the Tektelic Server which is pushed via MQTT, in base64, to an online broker.

> This repository contains `python` code which grabs the `MQTT` messages from the broker, `decodes` them, and pushes the decoded message back to the `MQTT` server as well as an `OPC-UA` server which the `PLC` can read the state from.

> Currently the sensor is sending messages infinitely so I can test my script and PLC implementation. These messages can be seen by running: `mqtt-OPCUA.py`
> Python packages needed:
- `paho.mqtt.client`
- `opcua`
- [`base64`][https://docs.python.org/3/library/base64.html]
