from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.cron.job_test_proxies_ping import start_ping
from src.cron.job_test_proxies_speed_test import start_speed_text
from src.config import Config
import threading

job_lock = threading.Lock()


def start_jobs(server, telegram_api):
    start_ping(job_lock, server, telegram_api, False)
    scheduler = BackgroundScheduler(
        {'apscheduler.job_defaults.max_instances': 3})
    # ping
    scheduler.add_job(
        lambda: start_ping(job_lock, server, telegram_api, False),
        trigger=CronTrigger.from_crontab(Config.cron_expression_ping)
    )

    # ping disconnected
    scheduler.add_job(
        lambda: start_ping(job_lock, server, telegram_api, True),
        trigger=CronTrigger.from_crontab(
            Config.cron_expression_ping_disconnect)
    )

    # speed test
    scheduler.add_job(
        lambda: start_speed_text(job_lock, server, telegram_api),
        trigger=CronTrigger.from_crontab(Config.cron_expression_speed_test)
    )

    scheduler.start()
