import logging

import redis

from .config import get_settings

logger = logging.getLogger(__name__)

_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """Un solo cliente por proceso: si se crea uno por request, el pool de
    conexiones queda abierto hasta que lo recolecte el GC."""
    global _client
    if _client is None:
        _client = redis.Redis.from_url(
            get_settings().redis_url,
            socket_connect_timeout=3,
            socket_timeout=3,  # sin esto, un Redis que acepta y no contesta cuelga /ready
        )
    return _client


def check_redis() -> bool:
    try:
        return bool(get_redis().ping())
    except Exception:
        logger.warning("Redis no responde", exc_info=True)
        return False
