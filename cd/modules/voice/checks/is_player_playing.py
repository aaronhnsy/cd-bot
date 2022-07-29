from __future__ import annotations

from typing import Literal

from discord.ext import commands
from discord.ext.commands._types import Check

from cd import custom, exceptions


__all__ = (
    "is_player_playing",
)


def is_player_playing() -> Check[custom.Context]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.player or not ctx.player.is_playing():
            raise exceptions.EmbedError(description="There are no tracks playing.")

        return True

    return commands.check(predicate)
