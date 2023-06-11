import redis

import os
from .apps.utils.core import is_testing

REDIS_HOST = os.getenv('REDIS_HOST','redis')
REDIS_PORT = 6380 if is_testing() else 6379
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
REDIS_INSTANCE = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1)
