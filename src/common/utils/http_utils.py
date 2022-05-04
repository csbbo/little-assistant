import logging

import aiohttp

logger = logging.getLogger(__name__)


async def request_get(url, timeout=5):
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            return await resp.text()
