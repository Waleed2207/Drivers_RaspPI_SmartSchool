import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import threading
import time
from motion_detection.gpio_manager import GPIOManager
from motion_detection.server_communicator import ServerCommunicator

class MotionSensorMonitor:
    def __init__(self, gpio_manager, server_communicator, space_id, room_id, room_name, device_id, raspberryPiIP, Control, user_oid):
        self.gpio_manager = gpio_manager
        self.server_communicator = server_communicator
        self.space_id = space_id
        self.room_id = room_id
        self.room_name = room_name
        self.device_id = device_id
        self.raspberryPiIP = raspberryPiIP
        self.user_oid = user_oid
        self.Control = Control
        self.manual_control = False
        self.led_status = False
        self.thread = threading.Thread(target=self.monitor_pir, daemon=True)
        self._retry_timer = None

    def monitor_pir(self):
        last_motion_time = None
        motion_detected = False
        while True:
            pir_value = self.gpio_manager.read_pir()
            if pir_value:
                last_motion_time = time.time()
                motion_detected = True
                if not self.led_status and not self.manual_control:
                    self.trigger_led_relay("on", "auto")
            elif motion_detected and (time.time() - last_motion_time > 60):
                motion_detected = False
                if not self.manual_control:
                    self.trigger_led_relay("off", "auto")
            time.sleep(0.1)
    
    def trigger_led_relay(self, state, Control):
        # Update the control attribute
        self.Control = Control
        
        # Check if the server is running using the server_communicator instance
        if not self.server_communicator.is_server_running():
            print("Server not running, cannot process light control request.")
            return

        server_approval, message = self.server_communicator.send_request_to_node(
            state, self.space_id, self.room_id, self.room_name, self.device_id, self.raspberryPiIP, self.Control, self.user_oid)

        if server_approval:
            if state == "on":
                self.gpio_manager.led_relay_on()
                self.led_status = True
                print("Light ON, Relay LOW")
            elif state == "off":
                self.gpio_manager.led_relay_off()
                self.led_status = False
                print("Light OFF, Relay HIGH")
        else:
            print(f"Failed to send '{state}' state request to Node server or server denied the action.")
            if "No new rules found" in message:
                print("Retrying in 30 seconds due to absence of new rules...")
                if self._retry_timer is None or not self._retry_timer.is_alive():
                    self._retry_timer = threading.Timer(30, self.trigger_led_relay, [state, Control])
                    self._retry_timer.start()

    def start_monitoring(self):
        self.thread.start()
    
    def set_manual_control(self, state):
        self.manual_control = state
