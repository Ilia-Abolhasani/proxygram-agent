import os
import requests


class Server:
    def __init__(self, agent_id):
        self.base_url = os.getenv("server_url")
        self.agent_id = agent_id

    def _get(self, url, query):
        response = requests.get(self.base_url + url, params=query)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Request failed with status code: {response.status_code}")
        return None

    def _post(self, url, query, body):
        response = requests.post(self.base_url + url, params=query, json=body)
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Request failed with status code: {response.status_code}")
        return None

    def _update(self, url, query, body):
        response = requests.put(self.base_url + url, params=query, json=body)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Request failed with status code: {response.status_code}")
        return None

    def _delete(self, url, query):
        response = requests.delete(self.base_url + url, params=query)
        if response.status_code == 204:  # Assuming 204 is the successful status code for a successful deletion
            print("Resource deleted successfully.")
        else:
            print(f"Request failed with status code: {response.status_code}")

    def get_ping_proxies(self):
        query = {}
        return self._get("/api/proxy/ping", query)

    def get_speed_test_proxies(self):
        query = {}
        return self._get("/api/proxy/ping", query)  # todo

    def send_report(self, proxies):
        query = {}
        body = proxies
        return self._post("/api/report", query, body)
