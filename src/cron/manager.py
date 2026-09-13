from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR
import src.cron.job_ping as job_ping
import src.cron.job_speed as job_speed
from src.config import Config
import time


def error_handler(server, event):
    exception_text = str(event.exception)
    traceback_text = str(event.traceback)

    message = f"{exception_text}\n\n{traceback_text}"
    server.send_log(message)
    print(event)


def start_jobs(server, telegram_api):
    while True:
        #job_ping.start_safe(server, telegram_api, False)        
        job_speed.start_safe(server, telegram_api)
    scheduler = BackgroundScheduler({"apscheduler.job_defaults.max_instances": 3})
    scheduler.add_listener(lambda event: error_handler(server, event), EVENT_JOB_ERROR)    
    # Schedules come from .env (cron_expression_*), which was already being
    # loaded into Config and then ignored here.
    scheduler.add_job(
        lambda: job_ping.start_safe(server, telegram_api, False),
        trigger=CronTrigger.from_crontab(Config.cron_expression_ping),
    )

    # ping disconnected proxies
    scheduler.add_job(
        lambda: job_ping.start_safe(server, telegram_api, True),
        trigger=CronTrigger.from_crontab(Config.cron_expression_ping_disconnect),
    )

    # speed test
    scheduler.add_job(
        lambda: job_speed.start_safe(server, telegram_api),
        trigger=CronTrigger.from_crontab(Config.cron_expression_speed_test),
    )

    scheduler.start()

    while True:
        time.sleep(60)
