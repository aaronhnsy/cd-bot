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
from cd import config, exceptions, objects, utilities


if TYPE_CHECKING:
    # Local
    from cd.bot import CD


__all__ = (
    "HTTPHandler",
    "WebSocketHandler",
)


# noinspection PyAttributeOutsideInit
class HTTPHandler(tornado.web.RequestHandler, abc.ABC):

    def initialize(self, bot: CD) -> None:  # type: ignore
        self.bot: CD = bot

    # Tokens

    def get_identifier(self) -> str:

        if _identifier := self.get_secure_cookie("identifier"):
            return _identifier.decode("utf-8")

        identifier: str = binascii.hexlify(os.urandom(32)).decode("utf-8")
        self.set_secure_cookie("identifier", identifier)

        return identifier

    async def get_token(self) -> objects.Token | None:

        identifier = self.get_identifier()

        if not (data := await self.bot.redis.hget("tokens", identifier)):
            return None

        token = objects.Token(json.loads(data))

        if token.has_expired:

            async with self.bot.session.post(
                    url="https://discord.com/api/oauth2/token",
                    data={
                        "client_secret": config.CLIENT_SECRET,
                        "client_id":     config.CLIENT_ID,
                        "redirect_uri":  config.REDIRECT_URI,
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

            token = objects.Token(data)
            await self.bot.redis.hset("tokens", identifier, token.json)

        return token

    # Users

    async def fetch_user(self) -> objects.User | None:

        if not (token := await self.get_token()):
            return None

        data = await self.bot.client.request(
            utilities.Route("GET", "/users/@me", token=token.access_token)
        )
        user = objects.User(data)

        identifier = self.get_identifier()
        await self.bot.redis.hset("users", identifier, user.json)

        return user

    async def get_user(self) -> objects.User | None:

        identifier = self.get_identifier()
        data = await self.bot.redis.hget("users", identifier)

        if data:
            user = objects.User(json.loads(data))
            if user.has_expired:
                user = await self.fetch_user()

        else:
            user = await self.fetch_user()

        return user

    # Guilds

    async def fetch_guilds(self) -> list[objects.Guild] | None:

        if not (token := await self.get_token()):
            return None

        if not (user := await self.get_user()):
            return

        data = await self.bot.client.request(
            utilities.Route("GET", "/users/@me/guilds", token=token.access_token)
        )
        guilds = [objects.Guild(guild) for guild in data]

        await self.bot.redis.hset("guilds", user.id, json.dumps([guild.json for guild in guilds]))

        return guilds

    async def get_guilds(self) -> list[objects.Guild] | None:

        if not (user := await self.get_user()):
            return

        data = await self.bot.redis.hget("guilds", user.id)

        if data:
            guilds = [objects.Guild(json.loads(guild)) for guild in json.loads(data)]
            if any(guild.has_expired for guild in guilds):
                guilds = await self.fetch_guilds()

        else:
            guilds = await self.fetch_guilds()

        return guilds

    async def get_related_guilds(self) -> dict[str, list[objects.Guild]]:

        user_guilds = await self.get_guilds() or []
        bot_guild_ids = [guild.id for guild in self.bot.guilds]

        return {
            "shared_guilds":     [guild for guild in user_guilds if guild.id in bot_guild_ids and guild.id not in config.BAD_GUILDS],
            "non_shared_guilds": [guild for guild in user_guilds if guild.id not in bot_guild_ids and guild.id not in config.BAD_GUILDS],
        }


# noinspection PyAttributeOutsideInit
class WebSocketHandler(tornado.websocket.WebSocketHandler, abc.ABC):

    def initialize(self, bot: CD) -> None:  # type: ignore
        self.bot: CD = bot
