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


def start_jobs(server, telegram_api_ping, telegram_api_speed):
    while True:
        for i in range(50):
            try:
                job_ping.start_safe(server, telegram_api_ping, False)
            except Exception as error:
                print(error)
            time.sleep(1)
        for i in range(10):
            try:
                job_ping.start_safe(server, telegram_api_ping, True)
            except Exception as error:
                print(error)
            time.sleep(1)
        for i in range(1):
            try:
                job_speed.start_safe(server, telegram_api_speed)
            except Exception as error:
                print(error)
            time.sleep(1)
        time.sleep(5)

    # scheduler = BackgroundScheduler({"apscheduler.job_defaults.max_instances": 3})
    # scheduler.add_listener(lambda event: error_handler(server, event), EVENT_JOB_ERROR)
    # # ping
    # scheduler.add_job(
    #     lambda: job_ping.start_safe(server, telegram_api_ping, False),
    #     trigger=CronTrigger.from_crontab(Config.cron_expression_ping),
    # )

    # # ping disconnected
    # scheduler.add_job(
    #     lambda: job_ping.start_safe(server, telegram_api_ping, True),
    #     trigger=CronTrigger.from_crontab(Config.cron_expression_ping_disconnect),
    # )

    # # speed test
    # scheduler.add_job(
    #     lambda: job_speed.start_safe(server, telegram_api_speed),
    #     trigger=CronTrigger.from_crontab(Config.cron_expression_speed_test),
    # )

    # scheduler.start()
