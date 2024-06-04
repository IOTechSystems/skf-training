from flask import Flask, render_template
import paho.mqtt.client as mqtt
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import time
import json

app = Flask(__name__)

# MQTT broker details
broker = "mqtt"  # Replace with your MQTT broker URL
port = 1883  # Replace with your MQTT broker port
topic1 = "xrt/devices/virtual/telemetry"  # Replace with your first MQTT topic
topic2 = "xrt/devices/s7/telemetry"  # Replace with your second MQTT topic
result_topic = "xrt/devices/virtual/request"  # Replace with your result MQTT topic

# Global variables to store the last received messages and countdown time
last_message_topic1 = 0
last_message_topic2 = 0
next_message_time = datetime.now()  + timedelta(seconds=10)
is_connected = False

# MQTT callback function
def on_message(client, userdata, msg):
    global last_message_topic1, last_message_topic2
    if msg.topic == topic1:
        value = get_value(msg.payload, "SineWaveWithOffsetAndPhase")
        if value is None:
            return
        last_message_topic1 = value
    elif msg.topic == topic2:
        value = get_value(msg.payload, "DB_1_I64")
        if value is None:
            return
        last_message_topic2 = value

def get_value(payload, res):
    try:
        message = json.loads(payload)
        if message is not None:
            readings = message.get("readings", {})
            if res in readings:
                value = readings[res].get("value")
                return value
        return None
    except Exception as e:
        print(f"An error occurred while extracting the value: {str(e)}")
        return None

# Function to multiply the values and publish the result
def multiply_and_publish():
    global mqttc
    global next_message_time
    try:
        value1 = float(last_message_topic1)
        value2 = float(last_message_topic2)
        result = value1 * value2
        next_message_time = datetime.now() + timedelta(seconds=10)
        payload = {
            "client": "example",
            "request_id": "1031",
            "op": "device:put",
            "type": "xrt.request:1.0",
            "device": "Virtual-Device",
            "values": {
                "StoreInt32Value": result
            }
        }
        mqttc.publish("xrt/devices/virtual/request", json.dumps(payload))
    except ValueError:
        next_message_time = datetime.now() + timedelta(seconds=10)
        pass

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global is_connected
    if rc == 0:
        print("Connected to MQTT broker")
        is_connected = True
        client.subscribe(topic1)
        client.subscribe(topic2)
    else:
        print(f"Failed to connect to MQTT broker, return code: {rc}")
        is_connected = False

# Create an MQTT client
mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message


try:
    mqttc.connect("mqtt", 1883, 60)
except ConnectionRefusedError:
    print("Connection to MQTT broker refused. Check if the broker is running.")


# Create a background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(multiply_and_publish, 'interval', seconds=10)
scheduler.start()

@app.route('/')
def index():
    countdown_time = (next_message_time - datetime.now()).total_seconds()
    return render_template('index.html', last_message_topic1=last_message_topic1,
                           last_message_topic2=last_message_topic2, countdown_time=countdown_time)

if __name__ == '__main__':
    mqttc.loop_start()
    app.run(host='0.0.0.0', port=8000)


