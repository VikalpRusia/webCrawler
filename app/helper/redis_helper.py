"""
Module to manage Redis cache and provide an abstraction to its core functionalities.
"""
import logging
from typing import List, Set, Union
import redis

from config.constants import CACHE_EXPIRY, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

logger = logging.getLogger(__name__)


class RedisHelper:
    """
    Helper class to interact with Redis cache.
    """

    def __init__(self):
        """
        Initialize the Redis connection.
        """
        try:
            self.conn = redis.Redis(
                host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True
            )
            logger.info("Connected to Redis successfully.")
        except redis.ConnectionError as ex:
            logger.error(f"Error connecting to Redis: {ex}")
            raise

    def push_list_to_key(self, key: str, values: List[str], ttl: int | None = CACHE_EXPIRY) -> None:
        """
        Store a list of values in a Redis list at the specified key and set TTL if provided.

        :param key: The Redis key.
        :param values: A list of values to store.
        :param ttl: Optional time-to-live (TTL) in seconds. Defaults to CACHE_EXPIRY.
        """
        if not isinstance(values, list):
            logger.error("Values must be a list.")
            return
        self.conn.rpush(key, *values)
        self.set_key_expiry(key, ttl)

    def set_key_value(self, key: str, value: str, ttl: int | None = CACHE_EXPIRY) -> None:
        """
        Store a single value in Redis with the specified key and set TTL if provided.

        :param key: The Redis key.
        :param value: The value to store.
        :param ttl: Optional time-to-live (TTL) in seconds. Defaults to CACHE_EXPIRY.
        """
        self.conn.set(key, value)
        self.set_key_expiry(key, ttl)

    def set_key_expiry(self, key: str, ttl: int | None = None) -> None:
        """
        Set a time-to-live (TTL) for the specified key.

        :param key: The Redis key.
        :param ttl: Optional time-to-live (TTL) in seconds. If None, no TTL is set.
        """
        if ttl is not None:
            if ttl <= 0:
                logger.error("TTL must be a positive integer.")
                return
            self.conn.expire(key, ttl)

    def get_value_by_key(self, key: str) -> str | None:
        """
        Retrieve the value associated with the specified key.

        :param key: The Redis key.
        :return: The value as a string, or None if the key does not exist.
        """
        return self.conn.get(key)

    def get_list_from_key(self, key: str) -> List[str]:
        """
        Retrieve the list of values stored at the specified key.

        :param key: The Redis key.
        :return: A list of values as strings. Returns an empty list if the key does not exist.
        """
        cached_list = self.conn.lrange(key, 0, -1)
        return [val for val in cached_list]

    def add_values_to_set(self, key: str, values: Union[str, List[str]], ttl: int | None = CACHE_EXPIRY) -> None:
        """
        Add one or more values to a Redis set at the specified key and set TTL if provided.

        :param key: The Redis key.
        :param values: A single value or a list of values to add.
        :param ttl: Optional time-to-live (TTL) in seconds. Defaults to CACHE_EXPIRY.
        """
        if isinstance(values, list):
            self.conn.sadd(key, *values)
        else:
            self.conn.sadd(key, values)
        self.set_key_expiry(key, ttl)

    def get_set_members(self, key: str) -> Set[str]:
        """
        Retrieve all members of a Redis set stored at the specified key.

        :param key: The Redis key.
        :return: A set of values as strings. Returns an empty set if the key does not exist.
        """
        cached_set = self.conn.smembers(key)
        return set(cached_set)

    def remove_key(self, key: str) -> None:
        """
        Remove the specified key from Redis.

        :param key: The Redis key.
        """
        self.conn.delete(key)
