from apscheduler.schedulers.background import BackgroundScheduler

from apscheduler.triggers.cron import CronTrigger

_scheduler = BackgroundScheduler()

def add_job(func, cron_expr: str, job_id: str):
    """Add a cron job for the given function."""
    trigger = CronTrigger.from_crontab(cron_expr)
    _scheduler.add_job(func, trigger, id=job_id)


def list_jobs():
    return _scheduler.get_jobs()


def remove_job(job_id: str):
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)


def start():
    if not _scheduler.running:
        _scheduler.start()


def stop():
    if _scheduler.running:
        _scheduler.shutdown()

