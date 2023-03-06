"""Module to connect to Redis."""

from typing import Optional

from redis.asyncio import Redis

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """Return Redis object to work with FastAPI."""
    return redis
