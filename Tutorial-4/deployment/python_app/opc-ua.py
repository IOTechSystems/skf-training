from flask import Flask, render_template
from opcua import Client
from opcua import ua
from datetime import datetime, timedelta
import json
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import joblib

allow_unsafe_werkzeug = True
app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# OPC-UA server details
server_url = "opc.tcp://localhost:4840"  # Replace with your OPC-UA server URL
rpm_path = "Objects.XRTInstances.virtual-server.virtual.Devices.Virtual-Device.Resources.CNCMillRPM"  # Replace with the browser path for CNCMillRPM
vibration_path = "Objects.XRTInstances.virtual-server.virtual.Devices.Virtual-Device.Resources.CNCMillVibration"  # Replace with the browser path for CNCMillVibration
temperature_path = "Objects.XRTInstances.virtual-server.virtual.Devices.Virtual-Device.Resources.CNCMillTemperature"  # Replace with the browser path for CNCMillTemperature
alarm_path = "Objects.XRTInstances.virtual-server.virtual.Devices.Virtual-Device.Resources.AlarmVariable"  # Replace with the browser path for the alarm variable

is_connected = False
values = [None, None, None]
alarm = False

# Load the model based on data within safe limits
def on_data_change(node, val, data):
    global values
    global alarm

    with open('model.pkl', 'rb') as file:
        loaded_model = joblib.load(file)

    if node.get_browse_name().to_string() == rpm_path:
        values[0] = val
    elif node.get_browse_name().to_string() == vibration_path:
        values[1] = val
    elif node.get_browse_name().to_string() == temperature_path:
        values[2] = val

    if values[0] is None or values[1] is None:
        return

    max_temperature = loaded_model.predict([[values[0], values[1]]])[0] * 1.1
    new_alarm = values[2] > max_temperature

    if new_alarm != alarm:
        alarm = new_alarm
        print(f"Alarm: {alarm}")
        alarm_node = client.get_node(alarm_path)
        alarm_node.set_value(ua.DataValue(ua.Variant(alarm, ua.VariantType.Boolean)))

    socketio.emit('update_values', {'values': values, 'alarm': bool(alarm)})

# Create an OPC-UA client
client = Client(server_url)

try:
    client.connect()
    print("Connected to OPC-UA server")
    is_connected = True

    # Create subscriptions for the desired nodes using browser paths
    sub = client.create_subscription(500, on_data_change)
    sub.subscribe_data_change([client.get_node(rpm_path), client.get_node(vibration_path), client.get_node(temperature_path)])

except Exception as e:
    print(f"Failed to connect to OPC-UA server: {str(e)}")
    is_connected = False

@app.route('/')
def index():
    return render_template('index.html', values=values,
                           alarm=alarm, isConnected=is_connected)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True)