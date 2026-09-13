import os
import time
import threading
import requests
from datetime import datetime, timezone
import hashlib
from src.config import Config

DEFAULT_TIMEOUT = 5
BATCH_TIMEOUT = 60
# A failing request used to fire off a log request of its own. When the server
# is already saturated that doubles the load it is failing under, so logs are
# rate limited and the suppressed ones are only counted.
LOG_MIN_INTERVAL = 30


class Server:
    def __init__(self):
        self.base_url = Config.server_url
        self.agent_id = Config.agent_id
        self.agent_secret = Config.agent_secret
        self._log_lock = threading.Lock()
        self._log_last_sent = 0.0
        self._log_suppressed = 0

    def _create_headers(self):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        message = f"{timestamp}{self.agent_secret}"
        hashed_timestamp = hashlib.sha256(message.encode()).hexdigest()

        headers = {"X-Request-Time": timestamp, "X-Hashed-Timestamp": hashed_timestamp}
        return headers

    def _get(self, url, query, sendLog=True, timeout=DEFAULT_TIMEOUT):
        headers = self._create_headers()
        response = None
        try:
            response = requests.get(
                self.base_url + url, params=query, headers=headers, timeout=timeout
            )
            if response.status_code == 200:
                data = response.json()
                return data
            raise Exception("Status_code is not 200.")
        except Exception as err:
            msg = f"""Request failed with status code: {response.status_code if response else ""}
                Method: GET
                Response: {response.text if response else ""}
                Url: {url}
                Query: {query}
                Exception: {err}"""
            print(msg)
            if sendLog:
                self.send_log(msg)
        return None

    def _post(self, url, query, body, sendLog=True, timeout=DEFAULT_TIMEOUT):
        headers = self._create_headers()
        response = None
        try:
            response = requests.post(
                self.base_url + url, params=query, json=body, headers=headers, timeout=timeout
            )
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                return data
            raise Exception("Status_code is not 200.")
        except Exception as err:
            msg = f"""
                Request failed with status code: {response.status_code if response else ""}
                Method: POST
                Response: {response.text if response else ""}
                Url: {url}
                Query: {query}
                Body: {body}
            """
            print(msg)
            if sendLog:
                self.send_log(msg)
        return None

    def _update(self, url, query, body, sendLog=True, timeout=DEFAULT_TIMEOUT):
        headers = self._create_headers()
        response = None
        try:
            response = requests.put(
                self.base_url + url, params=query, json=body, headers=headers, timeout=timeout
            )
            if response.status_code == 200:
                data = response.json()
                return data
            raise Exception("Status_code is not 200.")
        except Exception as err:
            msg = f"""
                Request failed with status code: {response.status_code if response else ""}
                Method: PUT
                Response: {response.text if response else ""}
                Url: {url}
                Query: {query}
                Body: {body}
            """
            print(msg)
            if sendLog:
                self.send_log(msg)
        return None

    def _delete(self, url, query, sendLog=True, timeout=DEFAULT_TIMEOUT):
        headers = self._create_headers()
        response = None
        try:
            response = requests.delete(
                self.base_url + url, params=query, headers=headers, timeout=timeout
            )
            if (
                response.status_code == 204
            ):  # Assuming 204 is the successful status code for a successful deletion
                print("Resource deleted successfully.")
                return
            raise Exception("Status_code is not 204.")
        except Exception as err:
            msg = f"""
                Request failed with status code: {response.status_code if response else ""}
                Method: DELETE
                Response: {response.text if response else ""}
                Url: {url}
                Query: {query}                
            """
            print(msg)
            if sendLog:
                self.send_log(msg)

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

    def soft_delete_proxy(self, proxy_id):
        query = {}
        return self._delete(f"/api/{self.agent_id}/proxy/delete/soft/{proxy_id}", query)

    def soft_delete_proxies(self, proxy_ids):
        query = {}
        body = {"proxy_ids": list(proxy_ids)}
        return self._post(
            f"/api/{self.agent_id}/proxy/delete/soft",
            query,
            body,
            timeout=BATCH_TIMEOUT,
        )

    def send_log(self, message):
        with self._log_lock:
            now = time.monotonic()
            if now - self._log_last_sent < LOG_MIN_INTERVAL:
                self._log_suppressed += 1
                return None
            suppressed = self._log_suppressed
            self._log_suppressed = 0
            self._log_last_sent = now
        if suppressed:
            message = f"[{suppressed} similar log(s) suppressed]\n{message}"
        query = {}
        body = {"message": message}
        return self._post(f"/api/{self.agent_id}/log/recive", query, body, False)
