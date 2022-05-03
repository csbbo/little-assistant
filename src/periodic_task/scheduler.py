import asyncio
import time
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from common.utils.tushare_utils import update_stocks_info


# scheduler.add_job(tick, 'interval', seconds=3)
def tick():
    print('Tick! The time is: %s' % datetime.now())


def run_scheduler(app):
    update_stocks_info(ts=app['ts'], db=app['db'])

    scheduler = AsyncIOScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(
        update_stocks_info,
        trigger='cron',
        day_of_week='mon-fri',
        hour=15,
        minute=30,
        kwargs={"ts": app['ts'], "db": app['db']}
    )
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass