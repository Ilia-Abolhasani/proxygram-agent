import concurrent.futures
from src.dot_dict import DotDict
from src.config import Config
import tqdm


def _create_packs(_array, pack_size):
    num_packs = len(_array) // pack_size
    if len(_array) % pack_size != 0:
        num_packs += 1

    packs = []
    for i in range(num_packs):
        start_idx = i * pack_size
        end_idx = start_idx + pack_size
        pack = _array[start_idx:end_idx]
        packs.append(pack)

    return packs


def task_function(telegram_api, proxy):
    print(f"started proxy: {proxy.id}")
    result = telegram_api.ping_proxy(proxy.td_proxy_id)
    return [result, proxy.id]


def start_ping(server, telegram_api):
    result = telegram_api.remove_all_proxies()
    result = server.get_ping_proxies()
    all_proxies = result['result']
    batch = Config.batch_size_ping
    pach_proxies = _create_packs(all_proxies, batch)
    for pack in tqdm.tqdm(pach_proxies):
        result = telegram_api.remove_all_proxies()
        # first add proxy to proxy list
        for i in range(0, len(pack)):
            proxy = DotDict(pack[i])
            result = telegram_api.add_proxy(
                proxy.server,
                proxy.port,
                proxy.secret)
            proxy.td_proxy_id = result.update['id']
            pack[i] = proxy
        # start paraller task
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for proxy in pack:
                futures.append(
                    executor.submit(
                        task_function,
                        telegram_api,
                        proxy)
                )
            # Wait for all tasks to complete
            concurrent.futures.wait(futures)
            reports = []
            for future in futures:
                [result, proxy_id] = future.result()
                seconds = -1
                if (not result.error):
                    seconds = result.update['seconds'] * 1000
                reports.append({
                    "proxy_id": proxy_id,
                    "ping": seconds
                })
            server.send_report({"reports": reports})
    result = telegram_api.remove_all_proxies()
