from typing import Any, NewType, TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    import asyncpg
    import redis.asyncio as aioredis
    from discord.ext import lava


__all__ = [
    "Database",
    "Redis",
    "Lavalink",
    "Colour",
    "FileSize",
]


# asyncpg
Database: TypeAlias = "asyncpg.Pool[asyncpg.Record]"

# redis
Redis: TypeAlias = "aioredis.Redis[Any]"

# lavalink
Lavalink: TypeAlias = "lava.Link[Any]"

# custom
Colour = NewType("Colour", str)
FileSize = NewType("FileSize", int)
