import src
from src.server import Server
from telegram.telegram_api import Telegram_API
from src.cron import manager
from src.config import Config


if __name__ == '__main__':
    server = Server()
    # telegram api for ping
    telegram_api_ping = Telegram_API(
        Config.telegram_app_id,
        Config.telegram_app_hash,
        Config.telegram_phone,
        Config.database_encryption_key,
        Config.tdlib_directory_ping,
        Config.start_mtproto_address,
        Config.start_mtproto_port,
        Config.start_mtproto_secret
    )
    telegram_api_ping.set_log_verbose_level(1)
    result = telegram_api_ping.remove_all_proxies()
    # telegram api for speed
    telegram_api_speed = Telegram_API(
        Config.telegram_app_id,
        Config.telegram_app_hash,
        Config.telegram_phone,
        Config.database_encryption_key,
        Config.tdlib_directory_speed,
        Config.start_mtproto_address,
        Config.start_mtproto_port,
        Config.start_mtproto_secret
    )
    telegram_api_speed.set_log_verbose_level(1)
    result = telegram_api_speed.remove_all_proxies()
    print("strat manager.")
    manager.start_jobs(server, telegram_api_ping, telegram_api_speed)
    telegram_api_ping.idle()
    telegram_api_speed.stop()
