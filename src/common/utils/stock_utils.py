from typing import Optional, List

from motor.motor_asyncio import AsyncIOMotorClient


async def query_stocks(db: AsyncIOMotorClient, search: str, includes: Optional[List] = None) -> list:
    if not includes:
        includes = ['ts_code', ]

    results = []
    flt = {'$or': [
        {'pinyin': {'$regex': search}},
        {'name': {'$regex': search}},
        {'ts_code': {'$regex': search}},
        {'symbol': {'$regex': search}},
    ]}
    stocks = await db.stocks.find(flt)
    for stock in stocks:
        results.append(
            {include: stock.get('include') for include in includes}
        )
    return results
