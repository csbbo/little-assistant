import logging
import time

import pypinyin
from tushare.pro.client import DataApi
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


async def update_stocks_info(ts: DataApi, db: AsyncIOMotorClient) -> None:
    logger.info("update stocks info start")
    start = time.time()

    fields = ['ts_code', 'symbol', 'name', 'area', 'industry', 'fullname', 'enname', 'market', 'exchange', 'curr_type',
              'list_status', 'list_date', 'delist_date', 'is_hs']
    fields_str = ','.join(fields)
    df = ts.query('stock_basic', exchange='', list_status='L', fields=fields_str)

    def short_pinyin(name):
        s = ''
        for letter in pypinyin.pinyin(name, style=pypinyin.Style.FIRST_LETTER, strict=False):
            s += letter[0][0]
        return s

    data = {}
    for _, row in df.iterrows():
        for field in fields:
            data[field] = row[field]
        data['pinyin'] = short_pinyin(row['name'])
        db.stocks.update_one({'ts_code': row['ts_code']}, {'$set': data}, upsert=True)

    spend_time = time.time() - start
    logger.info(f"update stocks info finish, {spend_time=}")
