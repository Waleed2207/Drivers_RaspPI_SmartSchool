import requests
import socket

class ServerCommunicator:
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def is_server_running(self):
        """Check if the server is running by attempting to connect to it."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(2)
                s.connect((self.address, int(self.port)))
                print("Server is running.")
                return True
            except socket.error as e:
                print(f"Server check failed: {e}")
                return False

    def send_request_to_node(self, state, space_id, room_id, device_id, raspberryPiIP):
        """Send a state change request to the Node.js server."""
        url = f"http://{self.address}:{self.port}/api-sensors/motion-detected"
        payload = {
            "state": state,
            "space_id": space_id,
            "room_id": room_id,
            "device_id": device_id,
            "raspberry_pi_ip": raspberryPiIP
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"Light {state} request successful: {response.status_code}")
                return True
            else:
                print(f"Request to Node.js server failed with status code {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Request to Node.js server failed: {e}")
            return False
