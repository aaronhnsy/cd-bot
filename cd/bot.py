# Standard Library
import collections
import logging

# Libraries
import asyncpg
import discord
from discord.ext import commands, lava
from redis import asyncio as aioredis

# Project
from cd import custom, objects, values
from cd.config import CONFIG
from cd.types import Database, Lavalink, Redis


__all__ = ["CD"]
__log__ = logging.getLogger("cd.bot")


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
        # webhooks
        self.guilds_webhook: discord.Webhook = discord.utils.MISSING
        self.commands_webhook: discord.Webhook = discord.utils.MISSING
        self.errors_webhook: discord.Webhook = discord.utils.MISSING

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
        await self._connect_postgresql()
        await self._connect_redis()
        await self._connect_lavalink()
        await self._load_extensions()
