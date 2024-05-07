from flask import Flask
from motion_detection.web_controller import WebController
from motion_detection.motion_sensor_monitor import MotionSensorMonitor
from motion_detection.server_communicator import ServerCommunicator
from routes.mindolife_route import iot_devices_blueprint
from routes.sensibo_route import sensibo_blueprint
import os
from dotenv import load_dotenv
from gpiozero import LED, OutputDevice, MotionSensor

app = Flask(__name__)
load_dotenv()
app.register_blueprint(iot_devices_blueprint, url_prefix='/api-mindolife')
app.register_blueprint(sensibo_blueprint, url_prefix='/api-sensibo')

# Device pin definitions
LED_PIN = 2  # BCM 2
RELAY_PIN = 27  # BCM 27
PIR_PIN = 17  # BCM 17

def create_app():
    NODE_SERVER_ADDRESS = os.getenv('NODE_SERVER_ADDRESS', '192.168.1.108')
    NODE_SERVER_PORT = os.getenv('NODE_SERVER_PORT', '8001')
    SPACE_ID = os.getenv('SPACE_ID', '17886285')  # Default or fetched from .env
    ROOM_ID = os.getenv('ROOM_ID', '17886285-1875')  
    DEVICE_ID = os.getenv('DEVICE_ID', '72710392') 
    # ClientIP = os.getenv('ClientIP', '10.100.102.24')
    ClientIP = os.getenv('ClientIP', '192.168.1.109')


    server_communicator = ServerCommunicator(NODE_SERVER_ADDRESS, NODE_SERVER_PORT)
    motion_sensor_monitor = MotionSensorMonitor(LED_PIN, RELAY_PIN, PIR_PIN, server_communicator, SPACE_ID, ROOM_ID, DEVICE_ID, ClientIP)

    web_controller = WebController(app, motion_sensor_monitor)
    motion_sensor_monitor.start_monitoring()

    return app

if __name__ == '__main__':
    app = create_app()
    # Run the Flask application
    try:
        app.run(debug=False, host='0.0.0.0', port=5009)
    except KeyboardInterrupt:
        print("Program stopped")

