from __future__ import annotations

# Standard Library
import dataclasses
from typing import TYPE_CHECKING, Self

# Libraries
import asyncpg
import dacite

# Project
from cd import utilities


if TYPE_CHECKING:
    # Project
    from cd.bot import CD


__all__ = ["UserData"]


@dataclasses.dataclass
class UserData:
    id: int

    @classmethod
    async def get(cls, bot: CD, _id: int) -> Self:
        # return user data from the cache if possible
        if _id in bot.user_data_cache:
            return bot.user_data_cache[_id]
        # otherwise, fetch it from the database, creating a new entry if necessary
        data: asyncpg.Record = await bot.database.fetchrow(  # pyright: ignore - data is always a record
            "INSERT INTO users (id) VALUES ($1) ON CONFLICT (id) DO UPDATE set id = $1 RETURNING *",
            _id
        )
        # convert the data into a user data object and cache it
        user_data = dacite.from_dict(cls, {**data}, config=utilities.DACITE_CONFIG)
        bot.user_data_cache[_id] = user_data
        # return the user data
        return user_data
