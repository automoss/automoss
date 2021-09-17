import redis


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
REDIS_INSTANCE = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
