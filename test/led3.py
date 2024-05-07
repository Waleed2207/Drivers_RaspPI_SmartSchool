from flask import Flask, render_template
from gpiozero import LED, OutputDevice, MotionSensor
import threading
import time
import requests
import socket
from dotenv import load_dotenv
import os

app = Flask(__name__, template_folder='/home/sameerzaher/Drivers_RaspPI_SmartSchool/templates')

# Load environment variables
load_dotenv()

# GPIO Pins using GPIO Zero (BCM numbering)
led = LED(2)  # Adjust as per your BCM setup, for GPIO 2
relay = OutputDevice(27, active_high=False, initial_value=True)  # Adjust as needed
pir = MotionSensor(17)  # Adjust as needed

# Node.js Server Address
NODE_SERVER_ADDRESS = os.getenv('NODE_SERVER_ADDRESS', '10.100.102.8')
NODE_SERVER_PORT = os.getenv('NODE_SERVER_PORT', '8001')

manual_control = False
led_status = False

def is_server_running(host, port):
    """Check if the Node.js server is running."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(2)
            s.connect((host, int(port)))
            s.close()
            print("Server is running.")
            return True
        except socket.error as e:
            print(f"Server check failed: {e}")
            return False

def send_request_to_node(state):
    """Send request to the Node.js server."""
    url = f"http://{NODE_SERVER_ADDRESS}:{NODE_SERVER_PORT}/api-sensors/motion-detected"
    try:
        response = requests.post(url, json={"state": state}, timeout=5)
        if response.status_code == 200:
            print(f"Light {state} request successful: {response.status_code}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"Request to Node.js server failed: {e}")
    return False

def led_relay_on():
    """Turn the LED and relay on."""
    global led_status
    if not led_status:
        server_running = is_server_running(NODE_SERVER_ADDRESS, NODE_SERVER_PORT)
        if server_running and send_request_to_node("on"):
            led.on()
            relay.on()
            led_status = True
            print("Bulb ON, Relay LOW")
        else:
            print("Cannot turn on the bulb. The server is down or unreachable.")

def led_relay_off():
    """Turn the LED and relay off."""
    global led_status
    if led_status:
        led.off()
        relay.off()
        led_status = False
        print("Bulb OFF, Relay HIGH")
        send_request_to_node("off")

def monitor_pir():
    global manual_control, led_status
    while True:
        if pir.wait_for_motion():
            print("Motion detected!")
            if not led_status and not manual_control:
                led_relay_on()
        if pir.wait_for_no_motion():
            print("No motion detected!")
            if not manual_control:
                led_relay_off()
        time.sleep(0.1)


@app.route("/")
def index():
    return render_template('index.html', manual_control=manual_control)

@app.route("/<action>", methods=['GET', 'POST'])
def action(action):
    global manual_control
    if action == "on":
        led_relay_on()
        manual_control = True
    elif action == "off":
        led_relay_off()
        manual_control = False
    elif action == "auto":
        manual_control = False
    return render_template('index.html', manual_control=manual_control)

if __name__ == '__main__':
    try:
        thread = threading.Thread(target=monitor_pir, daemon=True)
        thread.start()
        app.run(debug=False, host='0.0.0.0', port=5009)

    except KeyboardInterrupt:
        # Handle manual interruption (e.g., Ctrl+C) from the terminal
        print("Program stopped")

