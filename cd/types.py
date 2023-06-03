from __future__ import annotations

from typing import Any, NewType, TypeAlias

import asyncpg
import redis.asyncio as aioredis
from discord.ext import lava


__all__ = [
    "Database",
    "Redis",
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
