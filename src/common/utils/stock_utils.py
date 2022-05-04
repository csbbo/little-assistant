import logging
from typing import Optional, List

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


async def query_stocks(db: AsyncIOMotorClient, search: str) -> list:
    logger.info(f"query stocks {search=}")

    flt = {'$or': [
        {'pinyin': {'$regex': search}},
        {'name': {'$regex': search}},
        {'ts_code': {'$regex': search}},
        {'symbol': {'$regex': search}},
    ]}
    return await db.stocks.find(flt).to_list(None)
