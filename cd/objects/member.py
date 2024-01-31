from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import asyncpg
import dacite

from cd import utilities


if TYPE_CHECKING:
    # Project
    from cd.bot import CD


__all__ = ["MemberData"]


@dataclasses.dataclass
class MemberData:
    user_id: int
    guild_id: int

    @classmethod
    async def get(cls, bot: CD, user_id: int, guild_id: int) -> MemberData:
        # return member data from the cache if possible
        if (user_id, guild_id) in bot.member_data_cache:
            return bot.member_data_cache[(user_id, guild_id)]
        # otherwise, fetch it from the database, creating a new entry if necessary
        data: asyncpg.Record = await bot.database.fetchrow(  # pyright: ignore - data is always a record
            "INSERT INTO members (user_id, guild_id) VALUES ($1, $2) "
            "ON CONFLICT (user_id, guild_id)"
            "DO UPDATE SET user_id = $1, guild_id = $2 "
            "RETURNING *",
            user_id, guild_id
        )
        # convert the data into a member data object and cache it
        member_data = dacite.from_dict(cls, {**data}, config=utilities.DACITE_CONFIG)
        bot.member_data_cache[(user_id, guild_id)] = member_data
        # return the member data
        return member_data
