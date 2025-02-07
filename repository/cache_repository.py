from typing import Optional

from redisClient.redis_client import redis_client
from config.config import Config

config = Config()


def get_cache_entity(key: str) -> Optional[str]:
    if redis_client.exists(key):
        return redis_client.get(key)
    else:
        return None


def create_cache_entity(key: str, value: str):
    if not redis_client.exists(key):
        redis_client.setex(key, config.REDIS_TTL, value)


def update_cache_entity(key: str, value: str):
    if redis_client.exists(key):
        redis_client.setex(key, config.REDIS_TTL, value)


def remove_cache_entity(key: str):
    if redis_client.exists(key):
        redis_client.delete(key)


def is_key_exists(key: str) -> bool:
    return redis_client.exists(key)
