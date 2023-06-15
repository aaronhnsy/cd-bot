from __future__ import annotations

import dataclasses
from typing import Self, TYPE_CHECKING

import asyncpg
import dacite

from cd import utilities

if TYPE_CHECKING:
    from cd.bot import CD


__all__ = ["UserData"]


@dataclasses.dataclass
class UserData:
    id: int

    @classmethod
    async def get(cls, bot: CD, id: int) -> Self:
        # return user data from the cache if possible
        if id in bot.user_data_cache:
            return bot.user_data_cache[id]
        # otherwise, fetch it from the database, creating a new entry if necessary
        data: asyncpg.Record = await bot.database.fetchrow(  # pyright: ignore - data is always a record
            "INSERT INTO users (id) VALUES ($1) ON CONFLICT (id) DO UPDATE set id = $1 RETURNING *",
            id
        )
        # convert the data into a user data object and cache it
        user_data = dacite.from_dict(cls, {**data}, config=utilities.DACITE_CONFIG)
        bot.user_data_cache[id] = user_data
        # return the user data
        return user_data
