from __future__ import annotations

from typing import Literal

from discord.ext import commands
from discord.ext.commands._types import Check

from cd import custom, exceptions


__all__ = (
    "is_track_seekable",
)


def is_track_seekable() -> Check[custom.Context]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.player or not ctx.player.current or not ctx.player.current.is_seekable():
            raise exceptions.EmbedError(description="The current track is not seekable.")

        return True

    return commands.check(predicate)
