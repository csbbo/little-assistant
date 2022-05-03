import asyncio

import aiohttp


async def request_get(url, **kwargs):
    async with aiohttp.ClientSession(**kwargs) as session:
        async with session.get(url) as resp:
            return await resp.text()


async def main():
    resp = await request_get('https://qt.gtimg.cn/q=sh601628')
    print(resp)


if __name__ == '__main__':
    asyncio.run(main())
