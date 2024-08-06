"""
Module to manage Redis cache and provide an abstraction to its core functionalities.
"""
import logging
from typing import List, Set, Union

import redis.asyncio as redis

from config.constants import CACHE_EXPIRY, REDIS_URL

logger = logging.getLogger(__name__)


class RedisHelper:
    """
    Helper class to interact with Redis cache.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initialize the Redis connection.
        """
        if not hasattr(self, "conn"):
            self.conn = None

    async def connect(self):
        """
        Asynchronously initialize the Redis connection.
        """
        try:
            self.conn = await redis.Redis.from_url(
                REDIS_URL, encoding="utf-8", decode_responses=True
            )
            logger.info("Connected to Redis successfully.")
        except redis.RedisError as ex:
            logger.error(f"Error connecting to Redis: {ex}")
            raise

    async def _is_connection_valid(self) -> bool:
        """
        Check if the Redis connection is valid.
        """
        try:
            # Simple ping command to check if the connection is still alive
            return await self.conn.ping()
        except redis.RedisError:
            # Connection is not valid
            return False

    async def __aenter__(self):
        if self.conn is None or not await self._is_connection_valid():
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            await self.conn.close()
            self.conn = None
            logger.info("Redis connection closed.")

    async def close(self):
        """
        Close the Redis connection pool.
        """
        self.conn.close()
        await self.conn.wait_closed()
        logger.info("Redis connection closed.")

    async def push_list_to_key(
        self, key: str, values: List[str], ttl: int | None = CACHE_EXPIRY
    ) -> None:
        """
        Store a list of values in a Redis list at the specified key and set TTL if provided.

        :param key: The Redis key.
        :param values: A list of values to store.
        :param ttl: Optional time-to-live (TTL) in seconds. Defaults to CACHE_EXPIRY.
        """
        if not isinstance(values, list):
            logger.error("Values must be a list.")
            return
        await self.conn.rpush(key, *values)
        await self.set_key_expiry(key, ttl)

    async def set_key_value(
        self, key: str, value: str, ttl: int | None = CACHE_EXPIRY
    ) -> None:
        """
        Store a single value in Redis with the specified key and set TTL if provided.

        :param key: The Redis key.
        :param value: The value to store.
        :param ttl: Optional time-to-live (TTL) in seconds. Defaults to CACHE_EXPIRY.
        """
        await self.conn.set(key, value)
        await self.set_key_expiry(key, ttl)

    async def set_key_expiry(self, key: str, ttl: int | None = None) -> None:
        """
        Set a time-to-live (TTL) for the specified key.

        :param key: The Redis key.
        :param ttl: Optional time-to-live (TTL) in seconds. If None, no TTL is set.
        """
        if ttl is not None:
            if ttl <= 0:
                logger.error("TTL must be a positive integer.")
                return
            await self.conn.expire(key, ttl)

    async def get_value_by_key(self, key: str) -> str | None:
        """
        Retrieve the value associated with the specified key.

        :param key: The Redis key.
        :return: The value as a string, or None if the key does not exist.
        """
        return await self.conn.get(key)

    async def get_list_from_key(self, key: str) -> List[str]:
        """
        Retrieve the list of values stored at the specified key.

        :param key: The Redis key.
        :return: A list of values as strings. Returns an empty list if the key does not exist.
        """
        cached_list = await self.conn.lrange(key, 0, -1)
        return [val for val in cached_list]

    async def add_values_to_set(
        self, key: str, values: Union[str, List[str]], ttl: int | None = CACHE_EXPIRY
    ) -> None:
        """
        Add one or more values to a Redis set at the specified key and set TTL if provided.

        :param key: The Redis key.
        :param values: A single value or a list of values to add.
        :param ttl: Optional time-to-live (TTL) in seconds. Defaults to CACHE_EXPIRY.
        """
        if isinstance(values, list):
            await self.conn.sadd(key, *values)
        else:
            await self.conn.sadd(key, values)
        await self.set_key_expiry(key, ttl)

    async def get_set_members(self, key: str) -> Set[str]:
        """
        Retrieve all members of a Redis set stored at the specified key.

        :param key: The Redis key.
        :return: A set of values as strings. Returns an empty set if the key does not exist.
        """
        cached_set = await self.conn.smembers(key)
        return set(cached_set)

    async def is_set_members(self, key: str, value: str) -> bool:
        """
        Retrieve all members of a Redis set stored at the specified key.

        :param key: The Redis set key.
        :param value: To be looked in set.
        :return: True if the key exists in set, False otherwise.
        """
        return await self.conn.sismember(key, value)

    async def set_hash(
        self, key: str, mapping: dict, ttl: int | None = CACHE_EXPIRY
    ) -> None:
        """
        Store a dictionary in a Redis hash at the specified key and set TTL if provided.

        :param key: The Redis key.
        :param mapping: A dictionary where keys and values are strings.
        :param ttl: Optional time-to-live (TTL) in seconds. Defaults to CACHE_EXPIRY.
        """
        if not isinstance(mapping, dict):
            logger.error("Mapping must be a dictionary.")
            return
        if not all(
            isinstance(k, str) and isinstance(v, str) for k, v in mapping.items()
        ):
            logger.error("Both keys and values in the dictionary must be strings.")
            return
        await self.conn.hset(key, mapping)
        await self.set_key_expiry(key, ttl)

    async def get_hash(self, key: str) -> dict:
        """
        Retrieve all fields and values of the hash stored at the specified key.

        :param key: The Redis key.
        :return: A dictionary with field-value pairs. Returns an empty dictionary if the key does not exist.
        """
        cached_dict = await self.conn.hgetall(key)
        return dict(cached_dict)

    async def remove_key(self, key: str) -> None:
        """
        Remove the specified key from Redis.

        :param key: The Redis key.
        """
        await self.conn.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Check if the specified key exists in Redis.

        :param key: The Redis key.
        :return: True if the key exists, False otherwise.
        """
        return await self.conn.exists(key)
