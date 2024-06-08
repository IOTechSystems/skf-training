from flask import Flask, render_template
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import json
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt

allow_unsafe_werkzeug=True
app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


# MQTT broker details
broker = "mqtt"  # Replace with your MQTT broker URL
port = 1883  # Replace with your MQTT broker port
topic = "xrt/devices/virtual/telemetry"  # Replace with your first MQTT topic
result_topic = "xrt/devices/s7/request"  # Replace with your result MQTT topic
is_connected = False
error_message = ""
values = [None, None, None]
alarm = False

# Load the model based on data within safe limits


# MQTT callback function
def on_message(client, userdata, msg):
    global values
    global alarm
    with open('model.pkl', 'rb') as file:
        loaded_model = joblib.load(file)
    if msg.topic == topic:
        get_values(msg.payload)
        if(values[0] is None or values[1] is None):
            return
        max_temperature = loaded_model.predict([[values[0], values[1]]])[0] * 1.4
        new_alarm = max_temperature < values[2]
        print(max_temperature,"vs",values[2],"  -   ", str(new_alarm))
        if new_alarm != alarm:
            alarm = new_alarm
            payload ={
			"client": "example",
			"request_id": "1031",
			"op": "device:put",
			"type": "xrt.request:1.0",
			"device": "S7-Server",
			"values": {
			    "Alarm": alarm
			}
		    }
            client.publish(result_topic, json.dumps(payload))
        socketio.emit('update_values', {'values': values, 'alarm': bool(new_alarm)})

def get_values(payload):
    global values
    try:
        message = json.loads(payload)
        if message is not None:
            readings = message.get("readings", {})
            if "CNCMillRPM" in readings:
                values[0] = readings["CNCMillRPM"].get("value")
            if "CNCMillVibration" in readings:
                values[1] = readings["CNCMillVibration"].get("value")
            if "CNCMillTemperature" in readings:
                values[2] = readings["CNCMillTemperature"].get("value")
        return
    except Exception as e:
        print(f"An error occurred while extracting the value: {str(e)}")
        return


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global is_connected
    if rc == 0:
        print("Connected to MQTT broker")
        is_connected = True
        client.subscribe(topic)
    else:
        print(f"Failed to connect to MQTT broker, return code: {rc}")
        is_connected = False

# Create an MQTT client
mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message


try:
    mqttc.connect(broker, 1883, 60)
except ConnectionRefusedError:
    print("Connection to MQTT broker refused. Check if the broker is running.")


@app.route('/')
def index():
    return render_template('index.html', values=values,
                           alarm=alarm, isConnected=is_connected, errorMessage=error_message)

if __name__ == '__main__':
    mqttc.loop_start()
    socketio.run(app, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True)
