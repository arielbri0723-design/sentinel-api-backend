import redis

from .config import get_settings


def check_redis() -> bool:
    try:
        client = redis.Redis.from_url(get_settings().redis_url, socket_connect_timeout=3)
        return bool(client.ping())
    except Exception:
        return False
