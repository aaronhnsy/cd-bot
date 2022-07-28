# Future
from __future__ import annotations

# Standard Library
import abc
import binascii
import json
import os
from typing import TYPE_CHECKING

# Packages
import tornado.web
import tornado.websocket

# Local
from cd import config, exceptions
from cd.modules import dashboard
from cd.modules.dashboard.utilities import http


if TYPE_CHECKING:
    # Local
    from cd.bot import SkeletonClique


__all__ = (
    "HTTPHandler",
    "WebSocketHandler",
)


# noinspection PyAttributeOutsideInit
class HTTPHandler(tornado.web.RequestHandler, abc.ABC):

    def initialize(self, bot: SkeletonClique) -> None:  # type: ignore
        self.bot: SkeletonClique = bot

    # Tokens

    def get_identifier(self) -> str:

        if _identifier := self.get_secure_cookie("identifier"):
            return _identifier.decode("utf-8")

        identifier: str = binascii.hexlify(os.urandom(32)).decode("utf-8")
        self.set_secure_cookie("identifier", identifier)

        return identifier

    async def get_token(self) -> dashboard.Token | None:

        identifier = self.get_identifier()
        token_data: str | None = await self.bot.redis.hget("tokens", identifier)

        if not token_data:
            return None

        token = dashboard.Token(json.loads(token_data))

        if token.has_expired:

            async with self.bot.session.post(
                    url="https://discord.com/api/oauth2/token",
                    data={
                        "client_secret": config.DISCORD_CLIENT_SECRET,
                        "client_id":     config.DISCORD_CLIENT_ID,
                        "redirect_uri":  config.DASHBOARD_REDIRECT_URL,
                        "refresh_token": token.refresh_token,
                        "grant_type":    "refresh_token",
                        "scope":         "identify guilds",
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
            ) as response:

                if 200 < response.status > 206:
                    raise exceptions.HTTPException(response, json.dumps(await response.json()))

                data = await response.json()

            if data.get("error"):
                raise exceptions.HTTPException(response, json.dumps(data))

            token = dashboard.Token(data)
            await self.bot.redis.hset("tokens", identifier, token.json)

        return token

    # Users

    async def fetch_user(self) -> dashboard.User | None:

        if not (token := await self.get_token()):
            return None

        data = await self.bot.client.request(
            http.Route("GET", "/users/@me", token=token.access_token)
        )
        user = dashboard.User(data)

        identifier = self.get_identifier()
        await self.bot.redis.hset("users", identifier, user.json)

        return user

    async def get_user(self) -> dashboard.User | None:

        identifier = self.get_identifier()
        data: str | None = await self.bot.redis.hget("users", identifier)

        if data:
            user = dashboard.User(json.loads(data))
            if user.has_expired:
                user = await self.fetch_user()

        else:
            user = await self.fetch_user()

        return user

    # Guilds

    async def fetch_guilds(self) -> list[dashboard.Guild] | None:

        if not (token := await self.get_token()):
            return None

        if not (user := await self.get_user()):
            return

        data = await self.bot.client.request(
            http.Route("GET", "/users/@me/guilds", token=token.access_token)
        )
        guilds = [dashboard.Guild(guild) for guild in data]

        await self.bot.redis.hset("guilds", user.id, json.dumps([guild.json for guild in guilds]))

        return guilds

    async def get_guilds(self) -> list[dashboard.Guild] | None:

        if not (user := await self.get_user()):
            return

        data: str | None = await self.bot.redis.hget("guilds", user.id)

        if data:
            guilds = [dashboard.Guild(json.loads(guild)) for guild in json.loads(data)]
            if any(guild.has_expired for guild in guilds):
                guilds = await self.fetch_guilds()

        else:
            guilds = await self.fetch_guilds()

        return guilds

    async def get_related_guilds(self) -> dict[str, list[dashboard.Guild]]:

        user_guilds = await self.get_guilds() or []
        bot_guild_ids = [guild.id for guild in self.bot.guilds]

        return {
            "shared_guilds":     [guild for guild in user_guilds if guild.id in bot_guild_ids and guild.id not in config.BAD_GUILDS],
            "non_shared_guilds": [guild for guild in user_guilds if guild.id not in bot_guild_ids and guild.id not in config.BAD_GUILDS],
        }


# noinspection PyAttributeOutsideInit
class WebSocketHandler(tornado.websocket.WebSocketHandler, abc.ABC):

    def initialize(self, bot: SkeletonClique) -> None:  # type: ignore
        self.bot: SkeletonClique = bot
