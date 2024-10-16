from flask import Flask, jsonify, request

class WebController:
    def __init__(self, app, sensor_monitor):
        self.app = app
        self.sensor_monitor = sensor_monitor
        self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/<action>", "action", self.action, methods=['GET', 'POST'])

    def index(self):
        """Render the index page with the current manual control status."""
        return jsonify({"manual_control": self.sensor_monitor.manual_control})

    def action(self, action):
        """Handle actions from the web interface to control the system."""
        response = {}
        Control = request.json.get('Control', 'manual')

        if action == "on":
            self.sensor_monitor.trigger_led_relay("on", Control)
            self.sensor_monitor.set_manual_control(True)
            response["message"] = "Turned LED on."
        elif action == "off":
            self.sensor_monitor.trigger_led_relay("off", Control)
            self.sensor_monitor.set_manual_control(False)
            response["message"] = "Turned LED off."
        elif action == "auto":
            self.sensor_monitor.set_manual_control(False)
            response["message"] = "Switched to automatic mode."

        return jsonify(response)
