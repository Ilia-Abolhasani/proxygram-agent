"""
Step 1: Fetch all proxies from server and save to proxies.json
Run this with VPN ON.
"""

import json
from src.server import Server


def fetch_and_save():
    server = Server()

    print("Fetching proxies from server...")
    result = server.get_ping_proxies(False)

    if not result:
        print("Failed to fetch proxies from server.")
        return

    proxies = result["result"]
    if len(proxies) == 0:
        print("No proxies found.")
        return

    with open("proxies.json", "w") as f:
        json.dump(proxies, f, indent=2)

    print(f"Saved {len(proxies)} proxies to proxies.json")


if __name__ == "__main__":
    fetch_and_save()
