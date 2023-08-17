import os
import sys
import logging
from dotenv import load_dotenv
from server import Server
from TelegramAPI import TelegramAPI
import test_proxies
from config import Config

if __name__ == '__main__':
    load_dotenv()
    agent_id = os.getenv("agent_id")
    server = Server(agent_id)
    telegram_api = TelegramAPI()
    m, a = telegram_api.channel_hsitory("speed_test_channel", 10, None)
    mes = telegram_api.get_message(Config.chat_id, Config.message_id)
    proxies = server.get_ping_proxies()
    test_proxies.start(telegram_api, server, proxies, 4)
