import os

import redis


def get_redis_connect():
    """Возвращаем подключение к редису."""
    host = os.getenv('REDIS_HOST')
    port = os.getenv('REDIS_PORT')
    password = os.getenv('REDIS_PASSWORD')

    return redis.Redis(host=host, port=port, db=0, password=password)
