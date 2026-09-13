import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv()


def _int_env(name, default):
    """int() straight off os.getenv blew up at import time with a message that
    never said which variable was missing."""
    raw = os.getenv(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return int(str(raw).strip().strip('"').strip("'"))
    except ValueError:
        raise ValueError(f"config '{name}' must be an integer, got {raw!r}")


class Config:
    server_url = os.getenv("server_url")
    agent_id = os.getenv("agent_id")
    agent_secret = os.getenv("agent_secret")
    telegram_app_id = os.getenv("telegram_app_id")
    telegram_app_hash = os.getenv("telegram_app_hash")
    telegram_phone = os.getenv("telegram_phone")
    # mt proto
    use_start_proxy = os.getenv("use_start_proxy", "true").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    _start_mtproto = os.getenv("start_mtproto")
    _parsed_url = urlparse(_start_mtproto)
    _query_params = parse_qs(_parsed_url.query)
    start_mtproto_address = _query_params.get("server", ["107.189.28.32"])[0]
    start_mtproto_port = int(_query_params.get("port", ["443"])[0])
    start_mtproto_secret = _query_params.get(
        "secret", ["eebe9ba010e83c95aa690b10c541d1db227777772e676f6f676c652e636f6d"]
    )[0]
    database_encryption_key = os.getenv("database_encryption_key")
    # single TDLib instance (fallback to old *_ping keys for backward compat)
    tdlib_directory = os.getenv("tdlib_directory") or os.getenv("tdlib_directory_ping")
    tdlib_lib_path = os.getenv("tdlib_lib_path") or os.getenv("tdlib_lib_path_ping")
    download_timeout = _int_env("download_timeout", 60)
    download_chat_id = os.getenv("download_chat_id")
    download_username = os.getenv("download_username")
    download_message_id = os.getenv("download_message_id")
    cron_expression_speed_test = os.getenv("cron_expression_speed_test") or "0 * * * *"
    cron_expression_ping = os.getenv("cron_expression_ping") or "*/5 * * * *"
    cron_expression_ping_disconnect = (
        os.getenv("cron_expression_ping_disconnect") or "*/30 * * * *"
    )
    batch_size_ping = _int_env("batch_size_ping", 64)
    batch_size_speed_test = _int_env("batch_size_speed_test", 16)
