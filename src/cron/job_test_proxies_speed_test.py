from src.dot_dict import DotDict
from src.config import Config
from src.util import create_packs

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


def _start(server, telegram_api, proxies):
    result = telegram_api.remove_all_proxies()
    batch = Config.batch_size_speed_test
    pack_proxies = create_packs(proxies, batch)
    for pack in tqdm.tqdm(pack_proxies):
        report_list = []
        for proxy in pack:
            proxy = DotDict(proxy)
            report = {"proxy_id": proxy.id}
            result = telegram_api.add_proxy(
                proxy.server,
                proxy.port,
                proxy.secret)
            td_proxy_id = result.update['id']
            result = telegram_api.enable_proxy(td_proxy_id)
            result = telegram_api.ping_proxy(td_proxy_id)
            seconds = -1
            if (not result.error):
                seconds = result.update['seconds'] * 1000
                report['download_speed'] = download_spped(telegram_api)
            result = telegram_api.remove_proxy(td_proxy_id)
            report['ping'] = seconds
            report_list.append(report)
        server.send_report({"reports": report_list})


def start_speed_text(job_lock, server, telegram_api):
    result = telegram_api.remove_all_proxies()
    result = server.get_speed_test_proxies()
    proxies = result['result']
    with job_lock:
        _start(server,
               telegram_api,
               proxies
               )
