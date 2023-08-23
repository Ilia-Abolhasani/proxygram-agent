from src.dot_dict import DotDict
from src.config import Config
import tqdm


def download_spped(telegram_api):
    result = telegram_api.get_message(
        Config.download_chat_id,
        Config.download_message_id)
    content = result.update["content"]
    document = content['document']
    document = document['document']
    file_id = document['id']
    return telegram_api.speed_test(file_id)


def _start(server, telegram_api, proxies, batch, speed_test):
    report_list = []
    for proxy in proxies:
        proxy = DotDict(proxy)
        report = {"proxy_id": proxy.id}
        result = telegram_api.add_proxy(
            proxy.server,
            proxy.port,
            proxy.secret)
        proxy_id = result.update['id']
        result = telegram_api.enable_proxy(proxy_id)
        result = telegram_api.ping_proxy(proxy_id)
        seconds = -1
        if (not result.error):
            seconds = result.update['seconds'] * 1000
            if (speed_test):
                report['download_speed'] = download_spped(telegram_api)
        result = telegram_api.remove_proxy(proxy_id)
        report['ping'] = seconds
        report_list.append(report)
        # upload
        if (len(report_list) >= batch):
            server.send_report({"reports": report_list})
            report_list = []
    if (len(report_list) > 0):
        server.send_report({"reports": report_list})


def _start(server, telegram_api, proxies, batch, speed_test):
    report_list = []
    for proxy in tqdm.tqdm(proxies):
        proxy = DotDict(proxy)
        report = {"proxy_id": proxy.id}
        result = telegram_api.add_proxy(
            proxy.server,
            proxy.port,
            proxy.secret)
        proxy_id = result.update['id']
        result = telegram_api.enable_proxy(proxy_id)
        result = telegram_api.ping_proxy(proxy_id)
        seconds = -1
        if (not result.error):
            seconds = result.update['seconds'] * 1000
            if (speed_test):
                report['download_speed'] = download_spped(telegram_api)
        result = telegram_api.remove_proxy(proxy_id)
        report['ping'] = seconds
        report_list.append(report)
        # upload
        if (len(report_list) >= batch):
            server.send_report({"reports": report_list})
            report_list = []
    if (len(report_list) > 0):
        server.send_report({"reports": report_list})


def create_packs(numbers, pack_size):
    num_packs = len(numbers) // pack_size
    if len(numbers) % pack_size != 0:
        num_packs += 1

    packs = []
    for i in range(num_packs):
        start_idx = i * pack_size
        end_idx = start_idx + pack_size
        pack = numbers[start_idx:end_idx]
        packs.append(pack)

    return packs


def start_ping(server, telegram_api):
    result = telegram_api.remove_all_proxies()
    result = server.get_ping_proxies()
    proxies = result['result']
    batch = Config.batch_size_speed_test,
    report_list = []
    counter = 0
    while (counter < len(proxies)):
        for proxy in range(0, ):
            counter += batch

    for proxy in tqdm.tqdm(proxies):
        proxy = DotDict(proxy)
        report = {"proxy_id": proxy.id}
        result = telegram_api.add_proxy(
            proxy.server,
            proxy.port,
            proxy.secret)
        proxy_id = result.update['id']
        result = telegram_api.enable_proxy(proxy_id)
        result = telegram_api.ping_proxy(proxy_id)
        seconds = -1
        if (not result.error):
            seconds = result.update['seconds'] * 1000
            if (speed_test):
                report['download_speed'] = download_spped(telegram_api)
        result = telegram_api.remove_proxy(proxy_id)
        report['ping'] = seconds
        report_list.append(report)
        # upload
        if (len(report_list) >= batch):
            server.send_report({"reports": report_list})
            report_list = []
    if (len(report_list) > 0):
        server.send_report({"reports": report_list})


def start_speed_text(job_lock, server, telegram_api):
    result = telegram_api.remove_all_proxies()
    result = server.get_speed_test_proxies()
    proxies = result['result']
    with job_lock:
        _start(server,
               telegram_api,
               proxies,
               Config.batch_size_speed_test,
               True)
