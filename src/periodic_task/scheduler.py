import asyncio
from datetime import datetime

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from common.utils.tushare_utils import update_stocks_info


# scheduler.add_job(tick, 'interval', seconds=3)
# def tick():
#     print('Tick! The time is: %s' % datetime.now())


def run_scheduler(app: aiohttp.web.Application):
    scheduler = AsyncIOScheduler(timezone='Asia/Shanghai')
    # scheduler.add_job(update_stocks_info, 'interval', seconds=10,  kwargs={"ts": app['ts'], "db": app['db']})
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
