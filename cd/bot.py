# Standard Library
import collections
import logging
from typing import Any

# Libraries
import aiohttp
import asyncpg
import discord
from discord.ext import commands, lava
from redis import asyncio as aioredis

# Project
from cd import custom, objects, values, webhooks
from cd.config import CONFIG


__all__ = ["CD"]
__log__ = logging.getLogger("cd.bot")

type Database = "asyncpg.Pool[asyncpg.Record]"
type Redis = "aioredis.Redis"
type Lavalink = lava.Link[Any]


class CD(commands.AutoShardedBot):

    def __init__(self) -> None:
        super().__init__(
            intents=values.INTENTS,
            allowed_mentions=values.ALLOWED_MENTIONS,
            status=values.STATUS,
            activity=values.ACTIVITY,
            help_command=custom.HelpCommand(),
            command_prefix=self.__class__._get_prefix,  # type: ignore
        )
        # connections
        self.session: aiohttp.ClientSession = discord.utils.MISSING
        self.webhooks: webhooks.WebhookManager = discord.utils.MISSING
        self.database: Database = discord.utils.MISSING
        self.redis: Redis = discord.utils.MISSING
        self.lavalink: Lavalink = discord.utils.MISSING
        # cache
        self.user_data_cache: dict[int, objects.UserData] = {}
        self.guild_data_cache: dict[int, objects.GuildData] = {}
        self.member_data_cache: dict[tuple[int, int], objects.MemberData] = {}
        # stats
        self.socket_stats: collections.Counter[str] = collections.Counter()
        self.command_stats: dict[str, collections.Counter[str]] = {
            "total":      collections.Counter(),
            "successful": collections.Counter(),
            "failed":     collections.Counter(),
        }

    async def _get_prefix(self, message: discord.Message) -> list[str]:
        if message.guild is not None:
            guild_data = await objects.GuildData.get(self, message.guild.id)
            prefixes = commands.when_mentioned_or(guild_data.prefix or CONFIG.discord.prefix)
        else:
            prefixes = commands.when_mentioned_or(CONFIG.discord.prefix)
        return prefixes(self, message)

    async def _connect_postgresql(self) -> None:
        try:
            __log__.debug("Attempting postgresql connection.")
            database: Database = await asyncpg.create_pool(  # pyright: ignore
                CONFIG.connections.postgresql.dsn,
                max_inactive_connection_lifetime=0,
                min_size=1, max_size=5,
            )
        except Exception as error:
            __log__.critical("Error while connecting to postgresql.")
            raise error
        else:
            __log__.info("Successfully connected to postgresql.")
            self.database = database

    async def _connect_redis(self) -> None:
        try:
            __log__.debug("Attempting redis connection.")
            redis: Redis = await aioredis.Redis.from_url(
                CONFIG.connections.redis.dsn,
                decode_responses=True, retry_on_timeout=True
            )
        except Exception as error:
            __log__.critical("Error while connecting to redis.")
            raise error
        else:
            __log__.info("Successfully connected to redis.")
            self.redis = redis

    async def _connect_lavalink(self) -> None:
        # TODO: Add support for multiple lavalink nodes.
        for link in CONFIG.discord.ext.lava.links:
            try:
                __log__.debug("Attempting lavalink connection.")
                lavalink: Lavalink = lava.Link(
                    host=link.host,
                    port=link.port,
                    password=link.password,
                    user_id=self.user.id,  # pyright: ignore
                    spotify_client_id=CONFIG.connections.spotify.client_id,
                    spotify_client_secret=CONFIG.connections.spotify.client_secret,
                )
                await lavalink.connect()
            except Exception as error:
                __log__.critical("Error while connecting to lavalink.")
                raise error
            else:
                __log__.info("Successfully connected to lavalink.")
                self.lavalink = lavalink

    async def _load_extensions(self) -> None:
        await self.load_extension("jishaku")
        await self.load_extension("cd.modules.errors")
        await self.load_extension("cd.modules.misc")
        await self.load_extension("cd.modules.stats")
        await self.load_extension("cd.modules.voice")

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        self.webhooks = webhooks.WebhookManager(self)
        await self._connect_postgresql()
        await self._connect_redis()
        await self._connect_lavalink()
        await self._load_extensions()

    async def close(self) -> None:
        await self.session.close()
        self.webhooks.loop.stop()
        if self.database:
            await self.database.close()
        if self.redis:
            await self.redis.close()
        if self.lavalink:
            await self.lavalink._reset_state()
        await super().close()
