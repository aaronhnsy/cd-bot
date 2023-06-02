from __future__ import annotations

from typing import NewType, TypeAlias

import asyncpg


__all__ = [
    "Pool",
    "Colour",
    "FileSize",
]

# asyncpg
Pool: TypeAlias = "asyncpg.Pool[asyncpg.Record]"

# custom
Colour = NewType("Colour", str)
FileSize = NewType("FileSize", int)
