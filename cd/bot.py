import logging

import asyncpg
import discord
from discord.ext import commands
from redis import asyncio as aioredis

from cd import objects, values
from cd.config import CONFIG
from cd.types import Pool, Redis


__all__ = ["CD"]
__log__ = logging.getLogger("cd.bot")


class CD(commands.AutoShardedBot):

    def __init__(self) -> None:
        super().__init__(
            intents=values.INTENTS,
            allowed_mentions=values.ALLOWED_MENTIONS,
            status=values.STATUS,
            activity=values.ACTIVITY,
            command_prefix=CONFIG.discord.prefix,
        )
        self.pool: Pool = discord.utils.MISSING
        self.redis: Redis = discord.utils.MISSING

        self.user_data_cache: dict[int, objects.UserData] = {}
        self.guild_data_cache: dict[int, objects.GuildData] = {}
        self.member_data_cache: dict[tuple[int, int], objects.MemberData] = {}

    async def _connect_postgresql(self) -> None:
        try:
            __log__.debug("Attempting postgresql connection.")
            pool: Pool = await asyncpg.create_pool(  # pyright: ignore
                CONFIG.connections.postgresql.dsn,
                max_inactive_connection_lifetime=0,
                min_size=1, max_size=5,
            )
        except Exception as error:
            __log__.critical("Error while connecting to postgresql.")
            raise error
        else:
            __log__.info("Successfully connected to postgresql.")
            self.pool = pool

    async def _connect_redis(self) -> None:
        try:
            __log__.debug("Attempting redis connection.")
            redis: Redis = await aioredis.Redis.from_url(  # pyright: ignore
                CONFIG.connections.redis.dsn,
                decode_responses=True, retry_on_timeout=True
            )
        except Exception as error:
            __log__.critical("Error while connecting to redis.")
            raise error
        else:
            __log__.info("Successfully connected to redis.")
            self.redis = redis

    async def setup_hook(self) -> None:
        await self._connect_postgresql()
        await self._connect_redis()
