from src.server import Server
from src.proxies_tg_wrapper.api_wrapper import Telegram_API
from src.cron import manager
from src.config import Config


if __name__ == "__main__":
    server = Server()
    # single TDLib instance shared by ping and speed jobs
    # (login is required because the speed test downloads a file from a chat)
    telegram_api = Telegram_API(
        Config.telegram_app_id,
        Config.telegram_app_hash,
        Config.telegram_phone,
        Config.database_encryption_key,
        Config.tdlib_directory,
        Config.tdlib_lib_path,
        Config.start_mtproto_address if Config.use_start_proxy else None,
        Config.start_mtproto_port if Config.use_start_proxy else None,
        Config.start_mtproto_secret if Config.use_start_proxy else None,
    )
    telegram_api.remove_all_proxies()
    telegram_api.set_log_verbose_level(1)
    print("start manager.")
    try:
        manager.start_jobs(server, telegram_api)
    finally:
        telegram_api.stop()
