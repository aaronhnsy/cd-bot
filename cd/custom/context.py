# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any

# Packages
import discord
from discord.ext import commands


if TYPE_CHECKING:
    # Local
    # noinspection PyUnresolvedReferences
    from cd.bot import SkeletonClique
    from cd.modules import voice


__all__ = (
    "Context",
)


class Context(commands.Context["SkeletonClique"]):

    @property
    def player(self) -> voice.Player | None:
        return getattr(self.guild, "voice_client", None)

    async def try_dm(self, *args: Any, **kwargs: Any) -> discord.Message | None:

        try:
            return await self.author.send(*args, **kwargs)
        except (discord.HTTPException, discord.Forbidden):
            try:
                return await self.reply(*args, **kwargs)
            except (discord.HTTPException, discord.Forbidden):
                return None
