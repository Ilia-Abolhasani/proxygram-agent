from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import app.cron.job_fetch_new_proxies as job_fetch_new_proxies


def start_jobs(context, telegram_api, bot_api):
    scheduler = BackgroundScheduler(daemon=True)
    job_fetch_new_proxies.start(context, telegram_api)
    # fetch_new_proxies
    # scheduler.add_job(
    #     lambda: job_fetch_new_proxies.start(context, telegram_api),
    #     trigger=CronTrigger.from_crontab('*/10 * * * *')
    # )
    #

    scheduler.start()
