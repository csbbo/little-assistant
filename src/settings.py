import os

HTTP_LISTEN = os.getenv('HTTP_LISTEN', '0.0.0.0')
HTTP_PORT = int(os.getenv('HTTP_PORT', '80'))
MONGODB_HOST = os.getenv('MONGODB_HOST', 'mongodb://la_mongo:27017/little_assistant')
# MONGODB_HOST = os.getenv('MONGODB_HOST', 'mongodb://127.0.0.1:27017/little_assistant')
# REDIS_HOST = os.getenv('REDIS_HOST', 'redis://127.0.0.1:6379/0')
# HASH_SALT = '94af841d6732b7bf1354aa753a9bd4faa'

TUSHARE_TOKE = os.getenv('TUSHARE_TOKE', '81fdd52d29ff8cfaccbbb9ae798a9982470de02f51198f5abd0f4b01')
