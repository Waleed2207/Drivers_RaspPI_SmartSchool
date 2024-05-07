from flask import request, jsonify
import requests
import os
import logging
# Ensure correct import path for Sensibo services
from services.sensibo_services import (
    fetch_ac_state_from_sensibo,
    fetch_temperature_data_from_sensibo,
    switch_ac_state,
    update_ac_mode
)
from controllers.base_controller_abstract import BaseController

class SensiboController(BaseController):
    def get(self):
        """Handles GET requests based on the URL endpoint to either fetch AC state or sensor data."""
        if request.path.endswith('/get_ac_state'):
            result = fetch_ac_state_from_sensibo()
            if result['success']:
                return jsonify(result), 200
            else:
                status_code = 404 if 'No AC state found' in result.get('message', '') else 500
                return jsonify(result), status_code
        elif request.path.endswith('/get_sensor_data'):
            result = fetch_temperature_data_from_sensibo()
            if result['success']:
                return jsonify(result), 200
            else:
                status_code = 404 if 'No measurements found' in result.get('message', '') else 500
                return jsonify(result), status_code

    def post(self):
        """Handles POST requests based on the URL endpoint to either switch AC state or update AC mode."""
        if request.path.endswith('/switch_ac_state'):
            try:
                data = request.json
                actual_device_id = data['id']
                actual_api_key = data['apiKey']
                state = data['state']
                temperature = data.get('temperature')  # Default to None if not provided
                result = switch_ac_state(actual_device_id, actual_api_key, state, temperature)
                return jsonify({"statusCode": 200, "data": result}), 200
            except ValueError as ve:
                return jsonify({"statusCode": 400, "error": str(ve)}), 400
            except Exception as e:
                return jsonify({"statusCode": 500, "error": str(e)}), 500

        elif request.path.endswith('/update_mode'):
            try:
                data = request.json
                device_id = data['deviceId']
                mode = data['mode']
                result = update_ac_mode(device_id, mode)
                return jsonify(result), 200
            except Exception as e:
                return jsonify({"success": False, "message": str(e)}), 500


