from __future__ import annotations

from typing import NewType, TypeAlias, Any

import asyncpg
import redis.asyncio as aioredis


__all__ = [
    "Pool",
    "Colour",
    "FileSize",
]

# asyncpg
Pool: TypeAlias = "asyncpg.Pool[asyncpg.Record]"

# redis
Redis: TypeAlias = "aioredis.Redis[Any]"

# custom
Colour = NewType("Colour", str)
FileSize = NewType("FileSize", int)
