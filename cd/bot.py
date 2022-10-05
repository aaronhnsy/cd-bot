from __future__ import annotations

import collections
import logging
import os
import time
from typing import Any

import aiohttp
import asyncpg
import discord
import mystbin
import tornado.httpserver
import tornado.web
from discord.ext import lava, commands, tasks
from redis import asyncio as aioredis

from cd import checks, custom, enums, manager, utilities, values
from cd.config import CONFIG
from cd.modules import voice, dashboard


LOG: logging.Logger = logging.getLogger("cd.bot")


class CD(commands.AutoShardedBot):

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
        self.redis: aioredis.Redis[Any] = utilities.MISSING
        self.lava: lava.Pool[CD, voice.Player] = utilities.MISSING
        self.mystbin: mystbin.Client = utilities.MISSING

        # logging
        self.logging_webhooks: dict[enums.LogType, discord.Webhook] = {
            enums.LogType.GUILD:   utilities.MISSING,
            enums.LogType.ERROR:   utilities.MISSING,
            enums.LogType.COMMAND: utilities.MISSING,
        }
        self.logging_queue: dict[enums.LogType, list[discord.Embed]] = collections.defaultdict(list)

        # tracking
        self.socket_stats: collections.Counter[str] = collections.Counter()
        self.manager: manager.Manager = manager.Manager(self)
        self.start_time: float = time.time()

        # dashboard
        self.dashboard: tornado.web.Application = utilities.MISSING
        self.http_server: tornado.httpserver.HTTPServer = utilities.MISSING
        self.http_client: dashboard.HTTPClient = utilities.MISSING

    def __repr__(self) -> str:
        return f"<CD id={self.user.id if self.user else values.BOT_ID}, users={len(self.users)}, guilds={self.guilds}>"

    # Setup

    async def connect_postgresql(self) -> None:

        try:
            LOG.debug("[POSTGRESQL] Attempting connection.")
            db = await asyncpg.create_pool(CONFIG.connections.postgres_dsn, max_inactive_connection_lifetime=0)

        except Exception as e:
            LOG.critical(f"[POSTGRESQL] Error while connecting.\n{e}\n")
            raise ConnectionError() from e

        assert db is not None

        LOG.info("[POSTGRESQL] Successful connection.")
        self.db = db

    async def connect_redis(self) -> None:

        try:
            LOG.debug("[REDIS] Attempting connection.")
            redis = aioredis.from_url(CONFIG.connections.redis_dsn, decode_responses=True, retry_on_timeout=True)

        except Exception as e:
            LOG.critical(f"[REDIS] Error while connecting.\n{e}\n")
            raise ConnectionError() from e

        LOG.info("[REDIS] Successful connection.")
        self.redis = redis

    async def connect_lava(self) -> None:

        self.lava = lava.Pool()

        for node in CONFIG.connections.discord_ext_lava_nodes:
            try:
                await self.lava.create_node(
                    bot=self,
                    provider=node.provider,
                    identifier=node.identifier,
                    host=node.host,
                    port=f"{node.port}",
                    password=node.password,
                    spotify_client_id=CONFIG.spotify.client_id,
                    spotify_client_secret=CONFIG.spotify.client_secret,
                )
            except Exception as error:
                LOG.error(f"[SLATE] Error while connecting to node '{node.identifier}'.")
                raise error

    async def load_extensions(self) -> None:

        for extension in values.EXTENSIONS:
            try:
                await self.load_extension(extension)
            except Exception as error:
                LOG.warning(f"[EXTENSIONS] Failed - {extension}")
                raise error

            LOG.info(f"[EXTENSIONS] Loaded - {extension}")

    async def setup_hook(self) -> None:

        self.add_check(checks.global_check, call_once=True)

        self.session = aiohttp.ClientSession()
        self.mystbin = mystbin.Client(session=self.session)

        self.logging_webhooks[enums.LogType.GUILD] = discord.Webhook.from_url(
            session=self.session,
            url=CONFIG.discord.guild_log_webhook
        )
        self.logging_webhooks[enums.LogType.ERROR] = discord.Webhook.from_url(
            session=self.session,
            url=CONFIG.discord.error_log_webhook
        )
        self.logging_webhooks[enums.LogType.COMMAND] = discord.Webhook.from_url(
            session=self.session,
            url=CONFIG.discord.command_log_webhook
        )
        self.log_task.start()

        await self.connect_postgresql()
        await self.connect_redis()
        await self.connect_lava()
        await self.load_extensions()

        if CONFIG.dashboard.enabled:

            self.dashboard = tornado.web.Application(
                dashboard.setup_routes(bot=self),
                static_path=os.path.join(os.path.dirname(__file__), "modules/dashboard/static/"),
                template_path=os.path.join(os.path.dirname(__file__), "modules/dashboard/src/html/"),
                cookie_secret=CONFIG.dashboard.cookie_secret,
                default_host=CONFIG.dashboard.host,
                debug=True
            )
            self.http_server = tornado.httpserver.HTTPServer(
                self.dashboard,
                xheaders=True
            )

            self.http_client = dashboard.HTTPClient(self.loop)
            await self.http_client.setup()

            self.http_server.bind(CONFIG.dashboard.port, CONFIG.dashboard.host)
            self.http_server.start()
            LOG.info("[DASHBOARD] Dashboard has connected.")

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
        cls: type[commands.Context[CD]] = utilities.MISSING
    ) -> commands.Context[CD]:
        return await super().get_context(message, cls=custom.Context)

    async def get_prefix(self, message: discord.Message) -> list[str]:

        if not message.guild:
            return commands.when_mentioned_or(CONFIG.general.prefix)(self, message)

        guild_config = await self.manager.get_guild_config(message.guild.id)
        return commands.when_mentioned_or(guild_config.prefix or CONFIG.general.prefix)(self, message)

    async def close(self) -> None:

        await self.session.close()

        if self.db:
            await self.db.close()
        if self.redis:
            await self.redis.close()

        await super().close()
