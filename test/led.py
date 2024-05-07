from flask import Flask, render_template
import RPi.GPIO as GPIO
import threading
import time
import requests

service_address='10.0.0.9'

app = Flask(__name__)

# GPIO Pins (BOARD numbering)
LED_PIN = 3    # Corresponds to GPIO 2
PIR_PIN = 11   # Corresponds to GPIO 17
RELAY_PIN = 13 # Relay PIN
manual_control = False
led_status = False

# GPIO setup
try:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)   # LED output pin
    GPIO.setup(RELAY_PIN, GPIO.OUT) # Relay output pin
    GPIO.setup(PIR_PIN, GPIO.IN)    # PIR sensor input pin
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Initialize Relay OFF

except Exception as e:
    print(f"Error accessing GPIO: {e}")

def led_relay_on():
    global led_status
    service_address = "10.0.0.9"  # Replace with your Node.js server address
    if not led_status:
        GPIO.output(LED_PIN, GPIO.HIGH)
        GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay ON
        print("Bulb ON, Relay LOW")
        led_status = True
        try:
            response = requests.post(f"http://{service_address}:5001/motion-detected", json={"state": "on"})
            print(f"Light ON request successful: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

def led_relay_off():
    global led_status
    service_address = "10.0.0.9"  # Replace with your Node.js server address
    if led_status:
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay OFF
        print("Bulb OFF, Relay HIGH")
        led_status = False
        try:
            response = requests.post(f"http://{service_address}:5001/motion-detected", json={"state": "off"})
            print(f"Light OFF request successful: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

def read_pir():
    return GPIO.input(PIR_PIN)

def monitor_pir():
    global manual_control, led_status
    last_motion_time = None
    motion_detected = False
    while True:
        pir_value = read_pir()
        if pir_value:
            last_motion_time = time.time()
            motion_detected = True
            if not led_status and not manual_control:
                led_relay_on()

        if motion_detected and (time.time() - last_motion_time > 10):
            motion_detected = False
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
	# Initialize the relay and LED to OFF state at the start
        led_relay_off()
        # Start a thread to monitor PIR sensor
        threading.Thread(target=monitor_pir, daemon=True).start()

        # Run the Flask web server
        app.run(debug=False, host='0.0.0.0', port=5009)

    except KeyboardInterrupt:
        # Handle manual interruption (e.g., Ctrl+C) from the terminal
        print("Program stopped")

    finally:
        # Cleanup GPIO pins when the program is stopped
        GPIO.cleanup()  # Clean up GPIO on exit or interrupt

