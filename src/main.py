import asyncio
import hashlib
import sys
import time

import aiohttp
import tushare
from aiohttp import web
import xml.etree.ElementTree as ET
import logging

from bson.codec_options import CodecOptions
from motor.motor_asyncio import AsyncIOMotorClient

import settings
from common.utils import stock_utils
from periodic_task.scheduler import run_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def request_get(url, **kwargs):
    async with aiohttp.ClientSession(**kwargs) as session:
        async with session.get(url) as resp:
            return await resp.text()


async def get_real_time_market(ts_code: str) -> tuple:
    """
    return: price, close
    """
    code, market = ts_code.split('.')
    q = f"{market.lower()}{code}"

    url = f"https://qt.gtimg.cn/q={q}"
    try:
        text = await request_get(url, timeout=5)
    except Exception as e:
        logger.error(str(e))
        return None, None

    price_list = text.split('~')
    return float(price_list[3]), price_list[32]


async def handle_check_token(request):
    token = "qazwsxedc123"  # 请按照公众平台官网\基本配置中信息填写

    signature = request.query.get('signature', '')
    timestamp = request.query.get('timestamp', '')
    nonce = request.query.get('nonce', '')
    echostr = request.query.get('echostr', '')
    logger.info(f"receive: {signature=}, {timestamp=}, {nonce=}, {echostr=},")

    hash_items = [token, timestamp, nonce]
    hash_items.sort()
    hash_items_str = "".join(hash_items)

    sha1 = hashlib.sha1()
    sha1.update(hash_items_str.encode('utf-8'))
    hashcode = sha1.hexdigest()
    logger.info(f"{hashcode=}")

    if hashcode == signature:
        logger.info("check success!")
        return web.Response(text=echostr)
    else:
        logger.info("check fail!")
        return web.Response(text="")


async def handle_receive_message(request):
    db = request.app['db']

    text = await request.text()
    logger.info(f"receive: {text=}")
    xml_data = ET.fromstring(text)

    msg_type = xml_data.find('MsgType').text
    if msg_type == 'text':
        message = xml_data.find('Content').text
        content = ''

        stocks = await stock_utils.query_stocks(db, message, includes=['name', 'ts_code'])
        for stock in stocks:
            price, _ = get_real_time_market(stock['ts_code'])
            content += f"{stock['name']} {price}"

        to_user_name = xml_data.find('FromUserName').text
        from_user_name = xml_data.find('ToUserName').text
        logger.info(f"{to_user_name=}, {from_user_name=}, {content=}")

        resp_xml = f"""
                    <xml>
                        <ToUserName><![CDATA[{to_user_name}]]></ToUserName>
                        <FromUserName><![CDATA[{from_user_name}]]></FromUserName>
                        <CreateTime>{int(time.time())}</CreateTime>
                        <MsgType><![CDATA[text]]></MsgType>
                        <Content><![CDATA[{content}]]></Content>
                    </xml>
                    """
        return web.Response(text=resp_xml)
    return web.Response(text="fail")


def add_routers(app):
    app.router.add_route(method='GET', path='/wx', handler=handle_check_token)
    app.router.add_route(method='POST', path='/wx', handler=handle_receive_message)


def create_app():
    app = web.Application(client_max_size=(1024 ** 2) * 10)

    db_client = AsyncIOMotorClient(settings.MONGODB_HOST, serverSelectionTimeoutMS=3000)
    db = db_client.get_database(codec_options=CodecOptions(tz_aware=True))
    app['db'] = db

    ts = tushare.pro_api(settings.TUSHARE_TOKE)
    app['ts'] = ts

    add_routers(app)
    return app


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'scheduler':
            run_scheduler(create_app())
    else:
        web.run_app(create_app(), host=settings.HTTP_LISTEN, port=settings.HTTP_PORT)
