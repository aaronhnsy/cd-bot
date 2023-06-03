from __future__ import annotations

import dataclasses
from typing import Self, TYPE_CHECKING

import asyncpg
import dacite

from cd import utilities

if TYPE_CHECKING:
    from cd.bot import CD


__all__ = ["GuildData"]


@dataclasses.dataclass
class GuildData:
    id: int
    prefix: str | None

    @classmethod
    async def get(cls, bot: CD, id: int) -> Self:
        # return guild data from the cache if possible
        if id in bot.guild_data_cache:
            return bot.guild_data_cache[id]
        # otherwise, fetch it from the database, creating a new entry if necessary
        data: asyncpg.Record = await bot.pool.fetchrow(  # pyright: ignore - is always a record
            "INSERT INTO guilds (id) VALUES ($1) ON CONFLICT (id) DO UPDATE set id = $1 RETURNING *",
            id
        )
        # convert the data into a guild data object and cache it
        guild_data = dacite.from_dict(cls, {**data}, config=utilities.DACITE_CONFIG)
        bot.guild_data_cache[id] = guild_data
        # return the guild data
        return guild_data
