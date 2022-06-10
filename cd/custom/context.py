# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any

# Packages
import discord
from discord.ext import commands

# Local
from cd import custom


if TYPE_CHECKING:
    # Local
    # noinspection PyUnresolvedReferences
    from cd.bot import CD


__all__ = (
    "Context",
)


class Context(commands.Context["CD"]):

    @property
    def player(self) -> custom.Player | None:
        return getattr(self.guild, "voice_client", None)

    async def try_dm(self, *args: Any, **kwargs: Any) -> discord.Message | None:

        try:
            return await self.author.send(*args, **kwargs)
        except (discord.HTTPException, discord.Forbidden):
            try:
                return await self.reply(*args, **kwargs)
            except (discord.HTTPException, discord.Forbidden):
                return None
