from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import src.cron as jobs
from src.config import Config


def start_jobs(server, telegram_api):
    scheduler = BackgroundScheduler(daemon=False)
    # ping
    scheduler.add_job(
        lambda: jobs.job_test_proxies.start_ping(server, telegram_api),
        trigger=CronTrigger.from_crontab(Config.cron_expression_ping)
    )

    # speed test
    scheduler.add_job(
        lambda: jobs.job_test_proxies.start_speed_text(server, telegram_api),
        trigger=CronTrigger.from_crontab(Config.cron_expression_speed_test)
    )

    scheduler.start()
