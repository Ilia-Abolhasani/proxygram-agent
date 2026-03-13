"""
Step 1: Fetch all proxies from server, filter by Iran IP, and save to proxies.json
Run this with VPN ON.

Requirements:
    pip install geoip2
    Place GeoLite2-Country.mmdb in the same directory as this script.
"""

import asyncio
import json
import socket

import geoip2.database

from src.server import Server

GEOIP_DB_PATH = "GeoLite2-Country.mmdb"
IRAN_COUNTRY_CODE = "IR"
DNS_TIMEOUT = 3  # seconds per lookup
CONCURRENCY = 500  # parallel DNS lookups
FILTER_IRAN_ONLY = True  # Set to False to skip country filtering


async def resolve_ip(loop: asyncio.AbstractEventLoop, server: str) -> str | None:
    try:
        results = await asyncio.wait_for(
            loop.getaddrinfo(server, None, family=socket.AF_INET),
            timeout=DNS_TIMEOUT,
        )
        return results[0][4][0]
    except Exception:
        return None


def get_country(reader: geoip2.database.Reader, ip: str) -> str | None:
    try:
        return reader.country(ip).country.iso_code
    except Exception:
        return None


async def check_proxy(
    loop: asyncio.AbstractEventLoop,
    reader: geoip2.database.Reader,
    proxy: dict,
    sem: asyncio.Semaphore,
) -> dict | None:
    server = proxy.get("server", "")
    raw_ip = proxy.get("ip")

    # If already an IP, skip DNS
    if raw_ip:
        ip = raw_ip
    else:
        async with sem:
            ip = await resolve_ip(loop, server)

    if not ip:
        return None

    if get_country(reader, ip) == IRAN_COUNTRY_CODE:
        return {**proxy, "ip": ip}
    return None


async def run(proxies: list) -> list:
    loop = asyncio.get_event_loop()
    sem = asyncio.Semaphore(CONCURRENCY)
    checked = 0
    iran_proxies = []

    with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
        tasks = [check_proxy(loop, reader, p, sem) for p in proxies]
        for coro in asyncio.as_completed(tasks):
            result = await coro
            checked += 1
            print(f"  {checked}/{len(proxies)} checked, {len(iran_proxies)} Iran found...", end="\r")
            if result:
                iran_proxies.append(result)

    return iran_proxies


def fetch_and_save():
    server = Server()

    print("Fetching proxies from server...")
    result = server.get_ping_proxies(False)

    if not result:
        print("Failed to fetch proxies from server.")
        return

    proxies = result["result"]
    if not proxies:
        print("No proxies found.")
        return

    if FILTER_IRAN_ONLY:
        print(f"Fetched {len(proxies)} proxies. Resolving and filtering by Iran IP...")
        iran_proxies = asyncio.run(run(proxies))
    else:
        print(f"Fetched {len(proxies)} proxies. Skipping country filter...")
        iran_proxies = proxies

    if FILTER_IRAN_ONLY:
        print(f"\nFound {len(iran_proxies)} Iran proxies out of {len(proxies)}")

    with open("proxies.json", "w") as f:
        json.dump(iran_proxies, f, indent=2)

    print(f"Saved {len(iran_proxies)} Iran proxies to proxies.json")


if __name__ == "__main__":
    fetch_and_save()
