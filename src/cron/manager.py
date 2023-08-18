from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.cron.job_test_proxies import start_ping, start_speed_text
from src.config import Config


def start_jobs(server, telegram_api):
    scheduler = BackgroundScheduler(daemon=False)
    start_ping(server, telegram_api)
    # ping
    # scheduler.add_job(
    #     lambda: start_ping(server, telegram_api),
    #     trigger=CronTrigger.from_crontab(Config.cron_expression_ping)
    # )

    # speed test
    # scheduler.add_job(
    #     lambda: start_speed_text(server, telegram_api),
    #     trigger=CronTrigger.from_crontab(Config.cron_expression_speed_test)
    # )

    # scheduler.start()
