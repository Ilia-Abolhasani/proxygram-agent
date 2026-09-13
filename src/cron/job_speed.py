import os
import time
from tqdm import tqdm
import concurrent.futures

from src.util import DotDict
from src.config import Config
from src.util import create_packs
from src.cron import job_lock, queue
from src.config import Config


def _remove_partial_download(result):
    try:
        path = ((result.update or {}).get("local") or {}).get("path")
    except Exception:
        path = None
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError as error:
            print(f"could not remove partial download {path}: {error}")


def download_spped(telegram_api):
    result = telegram_api.get_message(
        int(Config.download_chat_id),
        int(Config.download_message_id))
    if (result.error):
        print(result.error_info['message'])
    try:
        content = result.update["content"]
        document = content['document']
        document = document['document']
        file_id = document['id']
    except Exception as error:
        raise error
    # speed test
    result = None
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(
            lambda: telegram_api.download_file(file_id, 32))
        try:
            result = future.result(timeout=Config.download_timeout)
        except concurrent.futures.TimeoutError:
            cancelled = telegram_api.cancel_download_file(file_id, False)
            # Whatever was downloaded before the timeout stays on disk unless
            # it is removed here; on an hourly agent that fills the volume.
            _remove_partial_download(cancelled)
            return 0
    end_time = time.time()
    elapsed_time = end_time - start_time
    file_path = result.update['local']['path']
    size = result.update['size']
    if os.path.exists(file_path):
        os.remove(file_path)
    return round(size / elapsed_time / 1000, 2)


def _start(server, telegram_api, proxies):
    result = telegram_api.remove_all_proxies()
    batch = Config.batch_size_speed_test
    pack_proxies = create_packs(proxies, batch)
    for pack in tqdm(pack_proxies, desc="Packs"):
        print("job-speed start packet")
        start_time = time.time()

        report_list = []
        for proxy in tqdm(pack, desc="Proxies", leave=False):
            proxy = DotDict(proxy)
            report = {"proxy_id": proxy.id}
            result = telegram_api.add_proxy(
                proxy.server,
                proxy.port,
                proxy.secret)
            if (result.error):
                continue
            td_proxy_id = result.update['id']
            result = telegram_api.enable_proxy(td_proxy_id)
            result = telegram_api.ping_proxy(td_proxy_id)
            seconds = -1
            speed = 0
            if (not result.error):
                seconds = result.update['seconds'] * 1000
                speed = download_spped(telegram_api)
            result = telegram_api.remove_proxy(td_proxy_id)
            report['speed'] = speed
            report['ping'] = seconds
            report_list.append(report)
        if report_list and server.send_speed_report(
            {"reports": report_list}
        ) is None:
            print(f"WARNING: {len(report_list)} speed report(s) were not accepted")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"job-speed packet sent elapsed_time: {elapsed_time}")


def _start_speed(server, telegram_api):    
    result = telegram_api.remove_all_proxies()    
    result = server.get_speed_test_proxies()
    if not result:
        print("no result fetched.")
        return
    proxies = result['result']
    if (len(proxies) == 0):
        queue.speed_test = False
        return
    _start(server,
           telegram_api,
           proxies
           )


def start_safe(server, telegram_api):
    global queue
    if (queue.speed_test):
        return
    queue.speed_test = True
    try:
        # ping and speed share one TDLib instance -> never run them concurrently
        with job_lock:
            _start_speed(server, telegram_api)
    finally:
        queue.speed_test = False
