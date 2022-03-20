# Future
from __future__ import annotations

# Standard Library
import collections
import logging
import time
from typing import Any

# Packages
import aiohttp
import aioredis
import asyncpg
import discord
import mystbin
import psutil
import slate
from discord.ext import commands, tasks
# noinspection PyUnresolvedReferences
from discord.ext.alternatives import converter_dict as converter_dict

# My stuff
from cd import checks, config, converters, custom, enums, manager, objects, utilities, values


__log__: logging.Logger = logging.getLogger("cd.bot")


class CD(commands.AutoShardedBot):

    converters: dict[Any, Any]

    def __init__(self) -> None:
        super().__init__(
            status=discord.Status.dnd,
            activity=discord.Activity(type=discord.ActivityType.listening, name="you."),
            allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=True),
            help_command=custom.HelpCommand(),
            intents=discord.Intents.all(),
            command_prefix=self.__class__.get_prefix,
            case_insensitive=True,
            owner_ids=values.OWNER_IDS,
            owner_id=None,
        )

        # internals
        self.converters.update(
            {
                objects.ConvertedTime:   converters.TimeConverter,
                objects.ConvertedPrefix: converters.PrefixConverter,
                enums.EmbedSize:         converters.EnumConverter(enums.EmbedSize, "Embed size"),
            }
        )

        # external connections
        self.session: aiohttp.ClientSession = utilities.MISSING
        self.db: asyncpg.Pool = utilities.MISSING
        self.redis: aioredis.Redis = utilities.MISSING
        self.slate: slate.Pool[CD, custom.Context, custom.Player] = utilities.MISSING
        self.mystbin: mystbin.Client = utilities.MISSING

        self._LOG_WEBHOOKS: dict[enums.LogType, discord.Webhook] = {
            enums.LogType.DM:      utilities.MISSING,
            enums.LogType.GUILD:   utilities.MISSING,
            enums.LogType.ERROR:   utilities.MISSING,
            enums.LogType.COMMAND: utilities.MISSING,
        }
        self._LOG_QUEUE: dict[enums.LogType, list[discord.Embed]] = collections.defaultdict(list)

        # tracking
        self.socket_stats: collections.Counter[str] = collections.Counter()
        self.process: psutil.Process = psutil.Process()
        self.manager: manager.Manager = manager.Manager(self)
        self.start_time: float = time.time()

    # Setup

    async def connect_postgresql(self) -> None:

        try:
            __log__.debug("[POSTGRESQL] Attempting connection.")
            db = await asyncpg.create_pool(**config.POSTGRESQL, max_inactive_connection_lifetime=0)

        except Exception as e:
            __log__.critical(f"[POSTGRESQL] Error while connecting.\n{e}\n")
            raise ConnectionError()

        assert db is not None

        __log__.info("[POSTGRESQL] Successful connection.")
        self.db = db

    async def connect_redis(self) -> None:

        try:
            __log__.debug("[REDIS] Attempting connection.")
            redis = aioredis.from_url(url=config.REDIS, decode_responses=True, retry_on_timeout=True)

        except Exception as e:
            __log__.critical(f"[REDIS] Error while connecting.\n{e}\n")
            raise ConnectionError()

        __log__.info("[REDIS] Successful connection.")
        self.redis = redis

    async def connect_slate(self) -> None:

        self.slate = slate.Pool()

        for node in config.NODES:
            try:
                await self.slate.create_node(
                    slate.Provider.OBSIDIAN,
                    bot=self,
                    identifier=node["identifier"],
                    host=node["host"],
                    port=node["port"],
                    password=node["password"],
                    session=self.session,
                    spotify_client_id=config.SPOTIFY_CLIENT_ID,
                    spotify_client_secret=config.SPOTIFY_CLIENT_SECRET,
                )
            except Exception as error:
                __log__.error(f"[SLATE] Error while connecting to node '{node['identifier']}'.")
                raise error

    async def setup_extensions(self) -> None:

        for extension in values.EXTENSIONS:
            try:
                await self.load_extension(extension)
            except Exception as error:
                __log__.warning(f"[EXTENSIONS] Failed - {extension}")
                raise error

            __log__.info(f"[EXTENSIONS] Loaded - {extension}")

    async def setup_hook(self) -> None:

        self.add_check(checks.bot, call_once=True)

        self.session = aiohttp.ClientSession()

        self.mystbin = mystbin.Client(session=self.session)

        self._LOG_WEBHOOKS[enums.LogType.DM] = discord.Webhook.from_url(session=self.session, url=config.DM_WEBHOOK_URL)
        self._LOG_WEBHOOKS[enums.LogType.GUILD] = discord.Webhook.from_url(session=self.session, url=config.GUILD_WEBHOOK_URL)
        self._LOG_WEBHOOKS[enums.LogType.ERROR] = discord.Webhook.from_url(session=self.session, url=config.ERROR_WEBHOOK_URL)
        self._LOG_WEBHOOKS[enums.LogType.COMMAND] = discord.Webhook.from_url(session=self.session, url=config.COMMAND_WEBHOOK_URL)
        self.log_task.start()

        await self.connect_postgresql()
        await self.connect_redis()
        await self.connect_slate()
        await self.setup_extensions()

    # Logging

    @tasks.loop(seconds=4)
    async def log_task(self) -> None:

        for _type, queue in self._LOG_QUEUE.items():

            if not (embeds := [queue.pop(0) for _ in range(min(10, len(queue)))]):
                continue

            await self._LOG_WEBHOOKS[_type].send(embeds=embeds)

    async def log(
        self,
        _type: enums.LogType, /,
        *,
        embed: discord.Embed
    ) -> None:
        self._LOG_QUEUE[_type].append(embed)

    # Overridden methods

    async def get_context(
        self,
        message: discord.Message,
        *,
        cls: type[commands.Context[CD]] = utilities.MISSING
    ) -> commands.Context[CD]:
        return await super().get_context(message=message, cls=custom.Context)

    async def get_prefix(self, message: discord.Message) -> list[str]:

        if not message.guild:
            return commands.when_mentioned_or(config.PREFIX)(self, message)

        guild_config = await self.manager.get_guild_config(message.guild.id)
        return commands.when_mentioned_or(guild_config.prefix or config.PREFIX)(self, message)

    async def close(self) -> None:

        await self.session.close()

        if self.db:
            await self.db.close()
        if self.redis:
            await self.redis.close()

        await super().close()
