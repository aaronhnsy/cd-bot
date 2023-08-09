# Standard Library
from typing import TYPE_CHECKING, Any, TypeAlias


if TYPE_CHECKING:
    # Libraries
    import asyncpg
    import redis.asyncio as aioredis
    from discord.ext import lava


__all__ = [
    "Database",
    "Redis",
    "Lavalink",
]


# asyncpg
Database: TypeAlias = "asyncpg.Pool[asyncpg.Record]"

# redis
Redis: TypeAlias = "aioredis.Redis[Any]"

# lavalink
Lavalink: TypeAlias = "lava.Link[Any]"
