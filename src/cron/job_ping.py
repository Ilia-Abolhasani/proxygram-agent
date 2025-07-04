import time
import tqdm
import concurrent.futures

from src.util import DotDict, create_packs
from src.config import Config
from src.cron import job_lock, queue

SOFT_DELETE_DISCONNECTED = False


def _task_function(telegram_api, proxy):
    # print(f"started proxy: {proxy.id}")
    result = telegram_api.ping_proxy(proxy.td_proxy_id)
    return [result, proxy.id]


def _start(server, telegram_api, proxies):
    result = telegram_api.remove_all_proxies()
    batch = Config.batch_size_ping
    pack_proxies = create_packs(proxies, batch)
    for pack in tqdm.tqdm(pack_proxies):
        print("job-ping start packet")
        start_time = time.time()
        result = telegram_api.remove_all_proxies()
        # first add proxy to proxy list
        for i in range(0, len(pack)):
            proxy = DotDict(pack[i])
            proxy.error = False
            result = telegram_api.add_proxy(proxy.server, proxy.port, proxy.secret)
            if result.error:
                proxy.error = True
                pack[i] = proxy
                err = result.error_info["message"]
                if err == "Wrong proxy secret" or err == "Unsupported proxy secret":
                    print("send delete proxy request.")
                    server.delete_proxy(proxy.id)
                continue
            proxy.td_proxy_id = result.update["id"]
            pack[i] = proxy
        # start paraller task
        reports = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for proxy in pack:
                if proxy.error:
                    continue
                futures.append(executor.submit(_task_function, telegram_api, proxy))
            # Wait for all tasks to complete
            concurrent.futures.wait(futures)
            for future in futures:
                [result, proxy_id] = future.result()
                seconds = -1
                if not result.error:
                    seconds = result.update["seconds"] * 1000
                if SOFT_DELETE_DISCONNECTED and seconds == -1:
                    print(f"soft_delete_proxy: {proxy_id}")
                    server.soft_delete_proxy(proxy_id)
                else:
                    reports.append({"proxy_id": proxy_id, "ping": seconds})
            server.send_ping_report({"reports": reports})
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"job-ping packet sent elapsed_time: {elapsed_time}")
    result = telegram_api.remove_all_proxies()


def _start_ping(server, telegram_api, disconnect):
    result = server.get_ping_proxies(disconnect)
    if not result:
        print("no result fetched.")
        return
    proxies = result["result"]
    if len(proxies) == 0:
        return
    _start(server, telegram_api, proxies)


def start_safe(server, telegram_api, disconnect):
    global job_lock, queue
    if disconnect:
        if queue.ping_disconnect:
            return
        queue.ping_disconnect = True
        with job_lock:
            _start_ping(server, telegram_api, disconnect)
        queue.ping_disconnect = False
        return
    else:
        if queue.ping_connect:
            return
        queue.ping_connect = True
        with job_lock:
            _start_ping(server, telegram_api, disconnect)
        queue.ping_connect = False
        return
