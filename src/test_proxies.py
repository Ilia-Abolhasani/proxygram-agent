from DotDict import DotDict
from config import Config


def download_spped(telegram_api):
    telegram_api.speed_test()
    result = telegram_api.get_message(
        Config.download_chat_id,
        Config.download_message_id)
    content = result.update["content"]
    document = content['document']
    document = document['document']
    file_id = document['id']
    return telegram_api.speed_test(file_id)


def start(telegram_api, server, proxies, batch, speed_test):
    result = telegram_api.remove_all_proxies()
    report_list = []
    for proxy in proxies:
        report = {"proxy_id": proxy.id}
        proxy = DotDict(proxy)
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
        if (len(reports) >= batch):
            server.send_report({"reports": reports})
            reports = []
    if (len(reports) > 0):
        server.send_report({"reports": reports})
