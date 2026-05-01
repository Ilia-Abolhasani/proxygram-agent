"""
Step 2: Read proxies.json, check connectivity (ping via TDLib), save results to report.json
Run this with VPN OFF. No Telegram login needed.
"""

import json
import concurrent.futures
import tqdm

from src.proxies_tg_wrapper.api_wrapper import Telegram_API
from src.config import Config
from src.util import DotDict, create_packs


def check_proxies():
    # Load proxies
    try:
        with open("proxies.json", "r") as f:
            proxies = json.load(f)
    except FileNotFoundError:
        print("proxies.json not found. Run fetch_proxies.py first.")
        return

    if len(proxies) == 0:
        print("No proxies to check.")
        return

    print(f"Loaded {len(proxies)} proxies from proxies.json")

    # Init Telegram API WITHOUT login
    telegram_api = Telegram_API(
        Config.telegram_app_id,
        Config.telegram_app_hash,
        Config.telegram_phone,
        Config.database_encryption_key,
        Config.tdlib_directory_ping,
        Config.tdlib_lib_path_ping,
        Config.start_mtproto_address,
        Config.start_mtproto_port,
        Config.start_mtproto_secret,
        skip_login=True,
    )
    telegram_api.set_log_verbose_level(1)
    telegram_api.remove_all_proxies()

    reports = []
    invalid_proxies = []
    batch = Config.batch_size_ping
    packs = create_packs(proxies, batch)

    for pack in tqdm.tqdm(packs, desc="Batches"):
        telegram_api.remove_all_proxies()

        # Add proxies to TDLib
        for i in range(len(pack)):
            proxy = DotDict(pack[i])
            proxy.error = False
            result = telegram_api.add_proxy(proxy.server, proxy.port, proxy.secret)
            if result.error:
                proxy.error = True
                pack[i] = proxy
                err = result.error_info["message"]
                if err == "Wrong proxy secret" or err == "Unsupported proxy secret":
                    invalid_proxies.append({"proxy_id": proxy.id, "reason": err})
                continue
            proxy.td_proxy_id = result.update["id"]
            pack[i] = proxy

        # Ping test in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for proxy in pack:
                if proxy.error:
                    continue
                futures.append(
                    executor.submit(
                        lambda p: [telegram_api.ping_proxy(p.td_proxy_id), p.id],
                        proxy,
                    )
                )
            concurrent.futures.wait(futures)

            for future in futures:
                [result, proxy_id] = future.result()
                ping_ms = -1
                if not result.error:
                    ping_ms = result.update["seconds"] * 1000
                reports.append({"proxy_id": proxy_id, "ping": ping_ms})

    telegram_api.remove_all_proxies()

    # Build report
    connected = [r for r in reports if r["ping"] >= 0]
    disconnected = [r for r in reports if r["ping"] < 0]

    report_data = {
        "reports": reports,
        "invalid_proxies": invalid_proxies,
        "summary": {
            "total": len(proxies),
            "connected": len(connected),
            "disconnected": len(disconnected),
            "invalid": len(invalid_proxies),
        },
    }

    with open("report.json", "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"\nResults saved to report.json")
    print(f"  Total: {len(proxies)}")
    print(f"  Connected: {len(connected)}")
    print(f"  Disconnected: {len(disconnected)}")
    print(f"  Invalid: {len(invalid_proxies)}")


if __name__ == "__main__":
    check_proxies()
