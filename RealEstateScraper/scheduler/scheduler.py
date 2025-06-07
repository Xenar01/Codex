from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def add_job(func, cron_expr):
    scheduler.add_job(func, 'cron', **cron_expr)


def start():
    if not scheduler.running:
        scheduler.start()


def stop():
    if scheduler.running:
        scheduler.shutdown()
