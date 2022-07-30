from __future__ import annotations

import collections
import logging
# import os
import time

import aiohttp
import aioredis
import asyncpg
import discord
import mystbin
import slate
# import tornado.httpserver
# import tornado.web
from discord.ext import commands, tasks

from cd import checks, config, custom, enums, manager, utilities, values
from cd.modules import voice
# from cd.modules import dashboard
# from cd.modules.dashboard.utilities import http


LOG: logging.Logger = logging.getLogger("cd.bot")


class SkeletonClique(commands.AutoShardedBot):

    def __init__(self) -> None:
        super().__init__(
            status=values.STATUS,
            activity=values.ACTIVITY,
            allowed_mentions=values.ALLOWED_MENTIONS,
            help_command=custom.HelpCommand(),
            intents=values.INTENTS,
            command_prefix=self.__class__.get_prefix,
            case_insensitive=True,
            owner_ids=values.OWNER_IDS,
            owner_id=None,
        )

        # external services
        self.session: aiohttp.ClientSession = utilities.MISSING
        self.db: asyncpg.Pool = utilities.MISSING
        self.redis: aioredis.Redis = utilities.MISSING
        self.slate: slate.Pool[SkeletonClique, voice.Player] = utilities.MISSING
        self.mystbin: mystbin.Client = utilities.MISSING

        # logging
        self.logging_webhooks: dict[enums.LogType, discord.Webhook] = {
            enums.LogType.Dm:      utilities.MISSING,
            enums.LogType.Guild:   utilities.MISSING,
            enums.LogType.Error:   utilities.MISSING,
            enums.LogType.Command: utilities.MISSING,
        }
        self.logging_queue: dict[enums.LogType, list[discord.Embed]] = collections.defaultdict(list)

        # tracking
        self.socket_stats: collections.Counter[str] = collections.Counter()
        self.manager: manager.Manager = manager.Manager(self)
        self.start_time: float = time.time()

        """
        # dashboard
        self.dashboard: tornado.web.Application = tornado.web.Application(
            dashboard.setup_routes(bot=self),
            static_path=os.path.join(os.path.dirname(__file__), "modules/dashboard/static/"),
            template_path=os.path.join(os.path.dirname(__file__), "modules/dashboard/templates/"),
            cookie_secret=config.DASHBOARD_COOKIE_SECRET,
            default_host=config.DASHBOARD_HOST,
            debug=True
        )
        self.server: tornado.httpserver.HTTPServer = tornado.httpserver.HTTPServer(
            self.dashboard,
            xheaders=True
        )
        self.client: http.HTTPClient = utilities.MISSING
        """

    def __repr__(self) -> str:
        return f"<SkeletonClique id={self.user.id if self.user else values.BOT_ID}, users={len(self.users)}, guilds={self.guilds}>"

    # Setup

    async def connect_postgresql(self) -> None:

        try:
            LOG.debug("[POSTGRESQL] Attempting connection.")
            db = await asyncpg.create_pool(**config.POSTGRESQL, max_inactive_connection_lifetime=0)

        except Exception as e:
            LOG.critical(f"[POSTGRESQL] Error while connecting.\n{e}\n")
            raise ConnectionError()

        assert db is not None

        LOG.info("[POSTGRESQL] Successful connection.")
        self.db = db

    async def connect_redis(self) -> None:

        try:
            LOG.debug("[REDIS] Attempting connection.")
            redis = aioredis.from_url(url=config.REDIS, decode_responses=True, retry_on_timeout=True)

        except Exception as e:
            LOG.critical(f"[REDIS] Error while connecting.\n{e}\n")
            raise ConnectionError()

        LOG.info("[REDIS] Successful connection.")
        self.redis = redis

    async def connect_slate(self) -> None:

        self.slate = slate.Pool()

        for node in config.NODES:
            try:
                await self.slate.create_node(
                    bot=self,
                    provider=slate.Provider.OBSIDIAN,
                    identifier=node["identifier"],
                    host=node["host"],
                    port=node["port"],
                    password=node["password"],
                    spotify_client_id=config.SPOTIFY_CLIENT_ID,
                    spotify_client_secret=config.SPOTIFY_CLIENT_SECRET,
                )
            except Exception as error:
                LOG.error(f"[SLATE] Error while connecting to node '{node['identifier']}'.")
                raise error

    async def setup_extensions(self) -> None:

        for extension in values.EXTENSIONS:
            try:
                await self.load_extension(extension)
            except Exception as error:
                LOG.warning(f"[EXTENSIONS] Failed - {extension}")
                raise error

            LOG.info(f"[EXTENSIONS] Loaded - {extension}")

    """
    async def start_dashboard(self) -> None:

        self.server.bind(config.DASHBOARD_PORT, config.DASHBOARD_HOST)
        self.server.start()

        LOG.info("[DASHBOARD] Dashboard has connected.")
    """

    async def setup_hook(self) -> None:

        self.add_check(checks.global_check, call_once=True)

        self.session = aiohttp.ClientSession()
        self.mystbin = mystbin.Client(session=self.session)
        # self.client = http.HTTPClient(self)

        self.logging_webhooks[enums.LogType.Dm] = discord.Webhook.from_url(
            session=self.session,
            url=config.DM_WEBHOOK_URL
        )
        self.logging_webhooks[enums.LogType.Guild] = discord.Webhook.from_url(
            session=self.session,
            url=config.GUILD_WEBHOOK_URL
        )
        self.logging_webhooks[enums.LogType.Error] = discord.Webhook.from_url(
            session=self.session,
            url=config.ERROR_WEBHOOK_URL
        )
        self.logging_webhooks[enums.LogType.Command] = discord.Webhook.from_url(
            session=self.session,
            url=config.COMMAND_WEBHOOK_URL
        )
        self.log_task.start()

        await self.connect_postgresql()
        await self.connect_redis()
        await self.connect_slate()
        # await self.start_dashboard()
        await self.setup_extensions()

    # Logging

    @tasks.loop(seconds=4)
    async def log_task(self) -> None:

        for _type, queue in self.logging_queue.items():

            if not (embeds := [queue.pop(0) for _ in range(min(10, len(queue)))]):
                continue

            await self.logging_webhooks[_type].send(embeds=embeds)

    async def log(self, log_type: enums.LogType, /, *, embed: discord.Embed) -> None:
        self.logging_queue[log_type].append(embed)

    # Overridden methods

    async def get_context(
        self,
        message: discord.Message | discord.Interaction,
        *,
        cls: type[commands.Context[SkeletonClique]] = utilities.MISSING
    ) -> commands.Context[SkeletonClique]:
        return await super().get_context(message, cls=custom.Context)

    async def get_prefix(self, message: discord.Message) -> list[str]:

        if not message.guild:
            return commands.when_mentioned_or(config.DISCORD_PREFIX)(self, message)

        guild_config = await self.manager.get_guild_config(message.guild.id)
        return commands.when_mentioned_or(guild_config.prefix or config.DISCORD_PREFIX)(self, message)

    async def close(self) -> None:

        await self.session.close()

        if self.db:
            await self.db.close()
        if self.redis:
            await self.redis.close()

        await super().close()
