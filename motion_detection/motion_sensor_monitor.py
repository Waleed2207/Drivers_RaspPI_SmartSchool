# motion_sensor_monitor.py

import threading
import time
from motion_detection.server_communicator import ServerCommunicator
from gpiozero import LED, OutputDevice, MotionSensor

class MotionSensorMonitor:
    def __init__(self, led_pin, relay_pin, pir_pin, server_communicator, space_id, room_id, device_id, raspberryPiIP):
        # Initialize GPIO devices using gpiozero within the class
        self.led = LED(led_pin)
        self.relay = OutputDevice(relay_pin, active_high=False)
        self.pir = MotionSensor(pir_pin)
        self.server_communicator = server_communicator
        self.space_id = space_id
        self.room_id = room_id
        self.device_id = device_id
        self.raspberryPiIP = raspberryPiIP
        self.manual_control = False
        self.led_status = False  # Track whether the LED and relay are currently on
        self.thread = threading.Thread(target=self.monitor_pir, daemon=True)

    def monitor_pir(self):
        last_motion_time = None
        motion_detected = False
        while True:
            pir_value = self.pir.motion_detected  # Directly use gpiozero's MotionSensor's property
            if pir_value:
                if not motion_detected:  # Only update if the state has changed
                    motion_detected = True
                    last_motion_time = time.time()
                    if not self.led_status and not self.manual_control:
                        self.trigger_led_relay("on")
            elif motion_detected and (time.time() - last_motion_time > 10):
                motion_detected = False
                if not self.manual_control:
                    self.trigger_led_relay("off")
            time.sleep(0.1)

    def trigger_led_relay(self, state):
        if state == "on" and self.server_communicator.is_server_running() and self.server_communicator.send_request_to_node(state, self.space_id, self.room_id, self.device_id, self.raspberryPiIP):
            self.led.on()
            self.relay.on()
            self.led_status = True  # Update status to reflect current state
            print("Bulb ON, Relay LOW")
        elif state == "off":
        # if not self.manual_control:
            self.led.off()
            self.relay.off()
            self.led_status = False  # Update status to reflect current state
            print("Bulb OFF, Relay HIGH")
            self.server_communicator.send_request_to_node(state, self.space_id, self.room_id, self.device_id, self.raspberryPiIP)

    def start_monitoring(self):
        self.thread.start()

    def set_manual_control(self, state):
        self.manual_control = state
