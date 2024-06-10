from flask import Flask, render_template
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import json
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt

app = Flask(__name__)
socketio = SocketIO(app)

# SocketIO event handler for client connection
@socketio.on('connect')
def handle_connect():
    print('Client connected')

# SocketIO event handler for client disconnection
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# MQTT broker details
broker = "mqtt"
port = 1883
topic = "xrt/devices/virtual/telemetry"
result_topic = "xrt/devices/s7/request"

# Global variables
is_connected = False
error_message = ""
values = [None, None, None]
alarm = False

# MQTT callback function for received messages
def on_message(client, userdata, msg):
    global values
    global alarm

    # Load the pre-trained model from file
    with open('model.pkl', 'rb') as file:
        loaded_model = joblib.load(file)

    if msg.topic == topic:
        # Extract values from the received message payload
        get_values(msg.payload)

        # Check if the required values are present
        if values[0] is None or values[1] is None:
            return

        # Predict the maximum temperature using the loaded model
        max_temperature = loaded_model.predict([[values[0], values[1]]])[0] * 1.4

        # Determine if an alarm should be triggered as the temperature is higher then max
        new_alarm = max_temperature < values[2]

	# if the value of the alarm has changed enter this if statement
        if new_alarm != alarm:
            alarm = new_alarm

            # Publish an MQTT message with the alarm value
            payload = {
                "client": "example",
                "request_id": "1031",
                "op": "device:put",
                "type": "xrt.request:1.0",
                "device": "S7-Server",
                "values": {
                    "Alarm": bool(alarm)
                }
            }
            client.publish(result_topic, json.dumps(payload))

            # Set the error message
            set_error_message(client, "Mill is too hot!")
        else:
            # Set the error message to "Good"
            set_error_message(client, "Good")

        # Emit the updated values and alarm state via SocketIO
        socketio.emit('update_values', {'values': values, 'alarm': bool(new_alarm)})

# Function to set the error message and publish it via MQTT and SocketIO
def set_error_message(client, msg):
    # Emit the error message via SocketIO
    socketio.emit('update_values', {'error_message': msg})

    # Publish the error message via MQTT
    payload = {
        "client": "example",
        "request_id": "1031",
        "op": "device:put",
        "type": "xrt.request:1.0",
        "device": "S7-Server",
        "values": {
            "Error_Message": str(msg)
        }
    }
    client.publish(result_topic, json.dumps(payload))

# Function to extract values from the received MQTT message payload
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

# MQTT callback function for successful connection
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

# Attempt to connect to the MQTT broker
try:
    mqttc.connect(broker, 1883, 60)
except ConnectionRefusedError:
    print("Connection to MQTT broker refused. Check if the broker is running.")

# Flask route for the root URL
@app.route('/')
def index():
    return render_template('index.html', values=values,
                           alarm=alarm, isConnected=is_connected, errorMessage=error_message)

# Run the Flask application with SocketIO
if __name__ == '__main__':
    mqttc.loop_start()
    socketio.run(app, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True)
