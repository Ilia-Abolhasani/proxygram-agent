import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    server_url = os.getenv("server_url")
    agent_id = os.getenv("agent_id")
    agent_secret = os.getenv("agent_secret")
    telegram_app_id = os.getenv("telegram_app_id")
    telegram_app_hash = os.getenv("telegram_app_hash")
    telegram_phone = os.getenv("telegram_phone")
    start_mtproto_address = os.getenv("start_mtproto_address")
    start_mtproto_port = os.getenv("start_mtproto_port")
    start_mtproto_secret = os.getenv("start_mtproto_secret")
    database_encryption_key = os.getenv("database_encryption_key")
    tdlib_directory_ping = os.getenv("tdlib_directory_ping")
    tdlib_directory_speed = os.getenv("tdlib_directory_speed")
    download_timeout = int(os.getenv("download_timeout"))
    download_chat_id = os.getenv("download_chat_id")
    download_message_id = os.getenv("download_message_id")
    cron_expression_speed_test = os.getenv(
        "cron_expression_speed_test")
    cron_expression_ping = os.getenv("cron_expression_ping")
    cron_expression_ping_disconnect = os.getenv(
        "cron_expression_ping_disconnect")
    batch_size_ping = int(os.getenv("batch_size_ping"))
    batch_size_speed_test = int(os.getenv("batch_size_speed_test"))
