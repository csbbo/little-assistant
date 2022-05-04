import hashlib
import logging
import sys
import time
import xml.etree.ElementTree as ET
from logging.config import dictConfig

import tushare
from aiohttp import web
from bson.codec_options import CodecOptions
from motor.motor_asyncio import AsyncIOMotorClient

import settings
from common.utils import stock_utils, tushare_utils
from periodic_task.scheduler import run_scheduler

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': "[%(asctime)s] [%(levelname)s] [%(threadName)s] [%(name)s: %(lineno)d] %(message)s"
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    }
}
dictConfig(LOGGING)
logger = logging.getLogger(__name__)


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

        stocks = await stock_utils.query_stocks(db, message)
        for stock in stocks:
            price = await tushare_utils.get_real_time_market(stock['ts_code'])
            content += f"{stock['name']} {price}"

        if not content:
            content = '查询失败'

        to_user_name = xml_data.find('FromUserName').text
        from_user_name = xml_data.find('ToUserName').text
        logger.info(f"reply message {to_user_name=}, {from_user_name=}, {content=}")

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
        web.run_app(
            create_app(),
            host=settings.HTTP_LISTEN,
            port=settings.HTTP_PORT,
            access_log=None
        )
