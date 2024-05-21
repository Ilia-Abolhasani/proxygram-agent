import os
import requests
from datetime import datetime, timezone
import hashlib
from src.config import Config


class Server:
    def __init__(self):
        self.base_url = Config.server_url
        self.agent_id = Config.agent_id
        self.agent_secret = Config.agent_secret

    def _create_headers(self):
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        message = f'{timestamp}{self.agent_secret}'
        hashed_timestamp = hashlib.sha256(message.encode()).hexdigest()

        headers = {
            'X-Request-Time': timestamp,
            'X-Hashed-Timestamp': hashed_timestamp
        }
        return headers

    def _get(self, url, query):
        headers = self._create_headers()
        response = requests.get(self.base_url + url,
                                params=query, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
        return None

    def _post(self, url, query, body):
        headers = self._create_headers()
        response = requests.post(
            self.base_url + url, params=query, json=body, headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Request failed with status code: {response.status_code}")
        return None

    def _update(self, url, query, body):
        headers = self._create_headers()
        response = requests.put(self.base_url + url,
                                params=query, json=body, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Request failed with status code: {response.status_code}")
        return None

    def _delete(self, url, query):
        headers = self._create_headers()
        response = requests.delete(
            self.base_url + url, params=query, headers=headers)
        if response.status_code == 204:  # Assuming 204 is the successful status code for a successful deletion
            print("Resource deleted successfully.")
        else:
            print(f"Request failed with status code: {response.status_code}")

    def get_ping_proxies(self, disconnect):
        query = {"disconnect": disconnect}
        return self._get(f"/api/{self.agent_id}/proxy/ping", query)

    def get_speed_test_proxies(self):
        query = {}
        return self._get(f"/api/{self.agent_id}/proxy/speed", query)

    def send_speed_report(self, proxies):
        query = {}
        body = proxies
        return self._post(f"/api/{self.agent_id}/report/speed", query, body)

    def send_ping_report(self, proxies):
        query = {}
        body = proxies
        return self._post(f"/api/{self.agent_id}/report/ping", query, body)

    def delete_proxy(self, proxy_id):
        query = {}
        return self._delete(f"/api/{self.agent_id}/proxy/delete/{proxy_id}", query)

    def send_log(self, message):
        query = {}
        body = {
            "message": message
        }
        return self._post(f"/api/{self.agent_id}/log/recive", query, body)
