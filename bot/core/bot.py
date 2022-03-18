# Future
from __future__ import annotations

# Standard Library
import collections
import logging
import time
import traceback
from typing import Any, Type

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
from core import config, values
from utilities import checks, custom, enums, utils


__log__: logging.Logger = logging.getLogger("bot")


async def get_prefix(bot: CD, message: discord.Message) -> list[str]:

    if not message.guild:
        return commands.when_mentioned_or(config.PREFIX)(bot, message)

    guild_config = await bot.config.get_guild_config(message.guild.id)
    return commands.when_mentioned_or(guild_config.prefix or config.PREFIX)(bot, message)


class CD(commands.AutoShardedBot):

    converters: dict[Any, Any]

    def __init__(self) -> None:
        super().__init__(
            status=discord.Status.dnd,
            activity=discord.Activity(type=discord.ActivityType.listening, name="you."),
            allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True, replied_user=False),
            help_command=custom.HelpCommand(),
            intents=discord.Intents.all(),
            command_prefix=get_prefix,
            case_insensitive=True,
            owner_ids=values.OWNER_IDS,
        )
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.socket_stats: collections.Counter[str] = collections.Counter()
        self.process: psutil.Process = psutil.Process()
        self.slate: slate.Pool[CD, custom.Context, custom.Player] = slate.Pool()
        self.mystbin: mystbin.Client = mystbin.Client(session=self.session)
        self.config: utils.Config = utils.Config(self)

        self.db: asyncpg.Pool = utils.MISSING
        self.redis: aioredis.Redis = utils.MISSING

        self.first_ready: bool = True
        self.start_time: float = time.time()

        self.log_webhooks: dict[enums.LogType, discord.Webhook] = {
            enums.LogType.DM:      discord.Webhook.from_url(session=self.session, url=config.DM_WEBHOOK_URL),
            enums.LogType.GUILD:   discord.Webhook.from_url(session=self.session, url=config.GUILD_WEBHOOK_URL),
            enums.LogType.ERROR:   discord.Webhook.from_url(session=self.session, url=config.ERROR_WEBHOOK_URL),
            enums.LogType.COMMAND: discord.Webhook.from_url(session=self.session, url=config.COMMAND_WEBHOOK_URL),
        }
        self.log_queue: dict[enums.LogType, list[discord.Embed]] = collections.defaultdict(list)

        self.converters |= values.CONVERTERS
        self.add_check(checks.bot, call_once=True)  # type: ignore
        self.log_loop.start()

    # Overridden methods

    async def get_context(self, message: discord.Message, *, cls: Type[commands.Context[CD]] = custom.Context) -> commands.Context[CD]:
        return await super().get_context(message=message, cls=cls)

    async def is_owner(self, user: discord.abc.User) -> bool:
        return user.id in values.OWNER_IDS

    async def start(self, token: str, *, reconnect: bool = True) -> None:

        try:
            __log__.debug("[POSTGRESQL] Attempting connection.")
            db: asyncpg.Pool = await asyncpg.create_pool(**config.POSTGRESQL, max_inactive_connection_lifetime=0)  # type: ignore
        except Exception as e:
            __log__.critical(f"[POSTGRESQL] Error while connecting.\n{e}\n")
            raise ConnectionError()
        else:
            __log__.info("[POSTGRESQL] Successful connection.")
            self.db = db

        try:
            __log__.debug("[REDIS] Attempting connection.")
            redis: aioredis.Redis = aioredis.from_url(url=config.REDIS, decode_responses=True, retry_on_timeout=True)
            await redis.ping()
        except (aioredis.ConnectionError, aioredis.ResponseError) as e:
            __log__.critical(f"[REDIS] Error while connecting.\n{e}\n")
            raise ConnectionError()
        else:
            __log__.info("[REDIS] Successful connection.")
            self.redis = redis

        for extension in values.EXTENSIONS:
            try:
                await self.load_extension(extension)
                __log__.info(f"[EXTENSIONS] Loaded - {extension}")
            except commands.ExtensionNotFound:
                __log__.warning(f"[EXTENSIONS] Extension not found - {extension}")
            except commands.NoEntryPointError:
                __log__.warning(f"[EXTENSIONS] No entry point - {extension}")
            except commands.ExtensionFailed as error:
                __log__.warning(f"[EXTENSIONS] Failed - {extension} - Reason: {traceback.print_exception(type(error), error, error.__traceback__)}")

        await super().start(token=token, reconnect=reconnect)

    async def close(self) -> None:

        await self.session.close()

        if self.db:
            await self.db.close()
        if self.redis:
            await self.redis.close()

        await super().close()

    # Events

    async def on_ready(self) -> None:

        if self.first_ready is False:
            return

        self.first_ready = False
        __log__.info(f"{self.user} is ready.")

        for node in config.NODES:
            try:
                await self.slate.create_node(
                    slate.Provider.OBSIDIAN,
                    bot=self,
                    identifier=node["identifier"],
                    host=node["host"],
                    port=node["port"],
                    password=node["password"],
                    spotify_client_id=config.SPOTIFY_CLIENT_ID,
                    spotify_client_secret=config.SPOTIFY_CLIENT_SECRET,
                )
            except slate.NodeConnectionError:
                continue

    # Logging

    @tasks.loop(seconds=3)
    async def log_loop(self) -> None:

        for type, queue in self.log_queue.items():

            if not (embeds := [queue.pop(0) for _ in range(min(10, len(queue)))]):
                continue

            await self.log_webhooks[type].send(embeds=embeds)

    async def log(self, type: enums.LogType, /, *, embed: discord.Embed) -> None:
        self.log_queue[type].append(embed)
