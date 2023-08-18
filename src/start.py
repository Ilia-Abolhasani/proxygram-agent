from server import Server
from Telegram import Telegram
from src.cron.manager import start_jobs
from config import Config

if __name__ == '__main__':
    server = Server(Config.agent_id)
    telegram_api = Telegram(
        Config.telegram_app_id,
        Config.telegram_app_hash,
        Config.telegram_phone,
        Config.database_encryption_key,
        Config.tdlib_directory,
        # Config.start_mtproto_address,
        # Config.start_mtproto_port,
        # Config.start_mtproto_secret
    )
    result = telegram_api.remove_all_proxies()
    proxies = server.get_ping_proxies()
    start_jobs(server, telegram_api)
