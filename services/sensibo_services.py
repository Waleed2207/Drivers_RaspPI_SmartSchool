import os
import requests
import logging
from dotenv import load_dotenv
load_dotenv() 

def fetch_ac_state_from_sensibo():
    """Fetches the AC state from the Sensibo API."""
    sensibo_device_id = os.getenv('SENSIBO_DEVICE_ID')
    sensibo_api_key = os.getenv('SENSIBO_API_KEY')
    url = f"https://home.sensibo.com/api/v2/pods/{sensibo_device_id}/acStates?apiKey={sensibo_api_key}&limit=1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        logging.debug("AC State Retrieved: %s", data)

        if data and 'result' in data and len(data['result']) > 0:
            return {'success': True, 'acState': data['result'][0].get('acState')}
        else:
            return {'success': False, 'message': "No AC state found"}

    except requests.HTTPError as e:
        logging.error(f"HTTP error occurred: {e.response.text}")
        return {'success': False, 'message': 'HTTP Error occurred', 'details': str(e)}
    except Exception as e:
        logging.error(f"Error retrieving AC state: {e}")
        return {'success': False, 'message': 'Error fetching data', 'details': str(e)}
        
def fetch_temperature_data_from_sensibo():
    """Fetches temperature and humidity measurements from the Sensibo API."""
    sensibo_device_id = os.getenv('SENSIBO_DEVICE_ID')
    if not sensibo_device_id:
        logging.error("SENSIBO_DEVICE_ID is not set.")
        return {'success': False, 'message': 'SENSIBO_DEVICE_ID is not set in environment variables'}

    sensibo_api_key = os.getenv('SENSIBO_API_KEY')
    if not sensibo_api_key:
        logging.error("SENSIBO_API_KEY is not set.")
        return {'success': False, 'message': 'SENSIBO_API_KEY is not set in environment variables'}

    url = f"https://home.sensibo.com/api/v2/pods/{sensibo_device_id}/measurements"

    try:
        response = requests.get(url, params={
            'fields': 'temperature,humidity',
            'apiKey': sensibo_api_key,
        })
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()

        if data and 'result' in data and len(data['result']) > 0:
            latest_measurements = data['result'][0]
            return {
                'success': True,
                'temperature': latest_measurements.get('temperature'),
                'humidity': latest_measurements.get('humidity')
            }
        else:
            logging.warning("No measurements found in the API response.")
            return {'success': False, 'message': "No measurements found"}

    except requests.HTTPError as e:
        logging.error(f"HTTP error occurred: {e.response.text}")
        return {'success': False, 'message': 'HTTP Error occurred', 'details': str(e)}
    except Exception as e:
        logging.error(f"General error fetching sensor data: {e}")
        return {'success': False, 'message': 'Error fetching data', 'details': str(e)}
    
def validate_degree(temperature):
    return 16 <= temperature <= 30

def switch_ac_state(actual_device_id, actual_api_key, state, temperature):
    device_url = f"https://home.sensibo.com/api/v2/pods/{actual_device_id}/acStates?apiKey={actual_api_key}"
    payload = {
        "acState": {
            "on": state,
            "targetTemperature": temperature,
            "mode": "cool"
        }
    }

    if temperature is not None and not validate_degree(temperature):
        raise ValueError("Temperature has to be between 16 and 30")

    response = requests.post(device_url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()  


def update_ac_mode(device_id, mode):
    api_key = os.getenv('SENSIBO_API_KEY')
    url = f"https://home.sensibo.com/api/v2/pods/{device_id}/acStates?apiKey={api_key}"
    payload = {
        "acState": {
            "on": True,
            "mode": mode,
        }
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return {"success": True, "data": response.json()}
    else:
        response.raise_for_status()