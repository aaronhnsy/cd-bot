from __future__ import annotations

from typing import TYPE_CHECKING, Any

import discord
from discord.ext import commands


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from cd.bot import CD
    from cd.modules import voice


__all__ = (
    "Context",
)


class Context(commands.Context["CD"]):

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
