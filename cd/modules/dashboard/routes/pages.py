# Future
from __future__ import annotations

# Standard Library
import abc
from typing import Any

# Packages
import discord
import pendulum

# Local
from cd.modules import dashboard
from cd.modules.dashboard.utilities import handlers


__all__ = (
    "Index",
    "Timezones",
    "Profile",
    "Servers",
    "Server"
)


# noinspection PyAsyncCall
class BasePage(handlers.HTTPHandler, abc.ABC):

    async def get_page_render_info(
        self,
        guild: dashboard.Guild | discord.Guild | None = None
    ) -> dict[str, Any]:

        user = await self.get_user()
        related_guilds = await self.get_related_guilds() if user is not None else {}

        return {
            "bot":   self.bot,
            "user":  user,
            "guild": guild,
            **related_guilds,
        }


# noinspection PyAsyncCall
class Index(BasePage, abc.ABC):

    async def get(self) -> None:  # type: ignore

        data = await self.get_page_render_info()

        self.render(
            "index.html",
            **data,
        )


# noinspection PyAsyncCall
class Timezones(BasePage, abc.ABC):

    async def get(self) -> None:  # type: ignore

        data = await self.get_page_render_info()

        self.render(
            "timezones.html",
            timezones=pendulum.timezones,
            **data,
        )


# noinspection PyAsyncCall
class Profile(BasePage, abc.ABC):

    async def get(self) -> None:  # type: ignore

        if not await self.get_user():
            self.set_status(401)
            return await self.finish({"error": "You must login to view this page."})

        data = await self.get_page_render_info()

        self.render(
            "profile.html",
            **data,
        )


# noinspection PyAsyncCall
class Servers(BasePage, abc.ABC):

    async def get(self) -> None:  # type: ignore

        if not await self.get_user():
            self.set_status(401)
            return await self.finish({"error": "You must login to view this page."})

        data = await self.get_page_render_info()

        self.render(
            "servers.html",
            **data,
        )


# noinspection PyAsyncCall
class Server(BasePage, abc.ABC):

    async def get(self, guild_id: str) -> None:  # type: ignore

        if not (user := await self.get_user()):
            self.set_status(401)
            return await self.finish({"error": "You must login to view this page."})

        if not (guild := self.bot.get_guild(int(guild_id))):
            self.set_status(400)
            await self.finish({"error": "i am not in this guild."})
            return

        if not guild.get_member(user.id):
            self.set_status(403)
            await self.finish({"error": "you are not in this guild."})
            return

        data = await self.get_page_render_info(
            guild=guild
        )

        self.render(
            "server.html",
            **data,
        )
