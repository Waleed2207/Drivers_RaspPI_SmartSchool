from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests
import socket

class ServerCommunicator:
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def is_server_running(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(2)
                s.connect((self.address, int(self.port)))
                s.close()
                print("Server is running.")
                return True
            except socket.error as e:
                print(f"Server check failed: {e}")
                return False

    def send_request_to_node(self, state, space_id, room_id, room_name, device_id, raspberryPiIP, Control, user_oid):
        url = f"http://{self.address}:{self.port}/api-sensors/motion-detected"
        payload = {
            "state": state,
            "space_id": space_id,
            "room_id": room_id,
            "room_name": room_name, 
            "device_id": device_id,
            "raspberry_pi_ip": raspberryPiIP,
            "control": Control,
            "user": user_oid
        }

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("http://", adapter)
        http.mount("https://", adapter)

        try:
            response = http.post(url, json=payload, timeout=10)
            response.raise_for_status()
            response_data = response.json()
            expected_message = f"Light turned {state}, request received successfully"
            if response_data.get('message') == expected_message:
                print(f"Light {state} request successful: {response.status_code}")
                return True, response_data.get('message')
            else:
                print(f"Failed to change state to {state}. Server response: {response_data.get('message', 'No message returned')}")
                return False, response_data.get('message')
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return False, str(http_err)
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
            return False, str(conn_err)
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
            return False, str(timeout_err)
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
            return False, str(req_err)
