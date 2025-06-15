import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv()


class Config:
    server_url = os.getenv("server_url")
    agent_id = os.getenv("agent_id")
    agent_secret = os.getenv("agent_secret")
    telegram_app_id = os.getenv("telegram_app_id")
    telegram_app_hash = os.getenv("telegram_app_hash")
    telegram_phone = os.getenv("telegram_phone")
    # mt proto
    _start_mtproto = os.getenv("start_mtproto")
    _parsed_url = urlparse(_start_mtproto)
    _query_params = parse_qs(_parsed_url.query)
    start_mtproto_address = _query_params.get("server", [""])[0]
    start_mtproto_port = int(_query_params.get("port", ["0"])[0])
    start_mtproto_secret = _query_params.get("secret", [""])[0]
    database_encryption_key = os.getenv("database_encryption_key")
    tdlib_directory_ping = os.getenv("tdlib_directory_ping")
    tdlib_lib_path_ping = os.getenv("tdlib_lib_path_ping")
    tdlib_directory_speed = os.getenv("tdlib_directory_speed")
    tdlib_lib_path_speed = os.getenv("tdlib_lib_path_speed")
    download_timeout = int(os.getenv("download_timeout"))
    download_chat_id = os.getenv("download_chat_id")
    download_username = os.getenv("download_username")
    download_message_id = os.getenv("download_message_id")
    cron_expression_speed_test = os.getenv("cron_expression_speed_test")
    cron_expression_ping = os.getenv("cron_expression_ping")
    cron_expression_ping_disconnect = os.getenv("cron_expression_ping_disconnect")
    batch_size_ping = int(os.getenv("batch_size_ping"))
    batch_size_speed_test = int(os.getenv("batch_size_speed_test"))
