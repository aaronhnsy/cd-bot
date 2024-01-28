from __future__ import annotations

# Standard Library
import dataclasses
from typing import TYPE_CHECKING

# Libraries
import asyncpg
import dacite

# Project
from cd import utilities


if TYPE_CHECKING:
    # Project
    from cd.bot import CD


__all__ = ["GuildData"]


@dataclasses.dataclass
class GuildData:
    id: int
    prefix: str | None

    @classmethod
    async def get(cls, bot: CD, _id: int) -> GuildData:
        # return guild data from the cache if possible
        if _id in bot.guild_data_cache:
            return bot.guild_data_cache[_id]
        # otherwise, fetch it from the database, creating a new entry if necessary
        data: asyncpg.Record = await bot.database.fetchrow(  # pyright: ignore - data is always a record
            "INSERT INTO guilds (id) VALUES ($1) ON CONFLICT (id) DO UPDATE set id = $1 RETURNING *",
            _id
        )
        # convert the data into a guild data object and cache it
        guild_data = dacite.from_dict(cls, {**data}, config=utilities.DACITE_CONFIG)
        bot.guild_data_cache[_id] = guild_data
        # return the guild data
        return guild_data
