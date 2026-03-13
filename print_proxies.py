"""Read proxies.json and print each proxy as a Telegram MTProto link."""

import json

with open("proxies.json") as f:
    proxies = json.load(f)

print(f"Total: {len(proxies)} proxies\n")

for p in proxies:
    server = p.get("server", "")
    port = p.get("port", "")
    secret = p.get("secret", "")
    print(f"https://t.me/proxy?server={server}&port={port}&secret={secret}")
