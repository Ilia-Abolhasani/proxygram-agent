import concurrent.futures
from src.dot_dict import DotDict
from src.config import Config
from src.util import create_packs

import tqdm


def _task_function(telegram_api, proxy):
    print(f"started proxy: {proxy.id}")
    result = telegram_api.ping_proxy(proxy.td_proxy_id)
    return [result, proxy.id]


def _start(server, telegram_api, proxies):
    result = telegram_api.remove_all_proxies()
    batch = Config.batch_size_ping
    pack_proxies = create_packs(proxies, batch)
    for pack in tqdm.tqdm(pack_proxies):
        result = telegram_api.remove_all_proxies()
        # first add proxy to proxy list
        for i in range(0, len(pack)):
            proxy = DotDict(pack[i])
            result = telegram_api.add_proxy(
                proxy.server,
                proxy.port,
                proxy.secret)
            if (result.error):
                print(result)
            proxy.td_proxy_id = result.update['id']
            pack[i] = proxy
        # start paraller task
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for proxy in pack:
                futures.append(
                    executor.submit(
                        _task_function,
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


def start_ping(job_lock, server, telegram_api, disconnect):
    try:
        result = server.get_ping_proxies(disconnect)
    except:
        return
    if not result:
        return
    all_proxies = result['result']
    if (len(all_proxies) == 0):
        return
    with job_lock:
        _start(server, telegram_api, all_proxies)
