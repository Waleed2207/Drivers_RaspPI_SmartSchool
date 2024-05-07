from gpiozero import LED, OutputDevice, MotionSensor

class GPIOManager:
    def __init__(self, led_pin, relay_pin, pir_pin):
        # Initialize GPIO devices using gpiozero
        self.led = LED(led_pin)  # GPIO pin for the LED
        self.relay = OutputDevice(relay_pin, active_high=False, initial_value=False)  # Active low relay
        self.pir = MotionSensor(pir_pin)  # GPIO pin for the PIR sensor
    
    def led_relay_on(self):
        """Turn the LED and relay on."""
        self.led.on()
        self.relay.on()  # Activate the relay (active low)
        print("LED and Relay are ON.")
    
    def led_relay_off(self):
        """Turn the LED and relay off."""
        self.led.off()
        self.relay.off()  # Deactivate the relay (active low)
        print("LED and Relay are OFF.")

    def monitor_pir(self):
        """Monitor the PIR sensor and control the LED and relay based on motion detection."""
        print("Monitoring PIR sensor. Press CTRL+C to exit.")
        self.pir.when_motion = self.led_relay_on
        self.pir.when_no_motion = self.led_relay_off