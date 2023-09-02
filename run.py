import src
from src.server import Server
from src.Telegram import Telegram
from src.cron import manager
from src.config import Config
import sys
import logging


def setup_logging(level=logging.INFO):
    root = logging.getLogger()
    root.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


if __name__ == '__main__':
    setup_logging(level=logging.ERROR)
    server = Server()
    # telegram api for ping
    telegram_api_ping = Telegram(
        Config.telegram_app_id,
        Config.telegram_app_hash,
        Config.telegram_phone,
        Config.database_encryption_key,
        Config.tdlib_directory_ping,
        Config.start_mtproto_address,
        Config.start_mtproto_port,
        Config.start_mtproto_secret
    )
    result = telegram_api_ping.remove_all_proxies()
    # telegram api for speed
    telegram_api_speed = Telegram(
        Config.telegram_app_id,
        Config.telegram_app_hash,
        Config.telegram_phone,
        Config.database_encryption_key,
        Config.tdlib_directory_speed,
        Config.start_mtproto_address,
        Config.start_mtproto_port,
        Config.start_mtproto_secret
    )
    result = telegram_api_speed.remove_all_proxies()
    manager.start_jobs(server, telegram_api_ping, telegram_api_speed)
    telegram_api_ping.idle()
    telegram_api_speed.stop()
