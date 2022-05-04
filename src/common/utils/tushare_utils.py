import logging
import time
from typing import Optional

import pypinyin
from tushare.pro.client import DataApi
from motor.motor_asyncio import AsyncIOMotorClient

from common.utils.http_utils import request_get

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


async def get_real_time_market(ts_code: str) -> Optional[float]:
    """
    return: price
    """
    code, market = ts_code.split('.')
    q = f"{market.lower()}{code}"

    url = f"https://qt.gtimg.cn/q={q}"
    try:
        text = await request_get(url, timeout=5)

        market_list = text.split('~')
        price = float(market_list[3])
        return price
    except Exception as e:
        logger.error(str(e))
        return None
