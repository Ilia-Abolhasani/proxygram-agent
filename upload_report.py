"""
Step 3: Read report.json and upload results to server.
Run this with VPN ON.
"""

import json
from src.server import Server


def upload():
    # Load report
    try:
        with open("report.json", "r") as f:
            report_data = json.load(f)
    except FileNotFoundError:
        print("report.json not found. Run run_offline.py first.")
        return

    server = Server()

    # Send ping report
    reports = report_data["reports"]
    if reports:
        print(f"Uploading {len(reports)} ping reports...")
        result = server.send_ping_report({"reports": reports})
        if result:
            print("Ping reports uploaded successfully.")
        else:
            print("Failed to upload ping reports.")

    # Delete invalid proxies
    invalid_proxies = report_data.get("invalid_proxies", [])
    if invalid_proxies:
        print(f"Deleting {len(invalid_proxies)} invalid proxies...")
        for proxy in invalid_proxies:
            server.delete_proxy(proxy["proxy_id"])
            print(f"  Deleted proxy {proxy['proxy_id']} ({proxy['reason']})")

    # Summary
    summary = report_data.get("summary", {})
    print(f"\nDone!")
    print(f"  Reports sent: {len(reports)}")
    print(f"  Invalid deleted: {len(invalid_proxies)}")
    print(f"  Connected: {summary.get('connected', '?')}")
    print(f"  Disconnected: {summary.get('disconnected', '?')}")


if __name__ == "__main__":
    upload()
