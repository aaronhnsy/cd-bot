# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Literal, TypeVar

# Packages
from discord.ext import commands

# Local
from cd import custom, exceptions


if TYPE_CHECKING:
    # Packages
    from discord.ext.commands._types import Check


__all__ = (
    "is_player_playing",
)


T = TypeVar("T")


def is_player_playing() -> Check[custom.Context]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.player or not ctx.player.is_playing():
            raise exceptions.EmbedError(description="There are no tracks playing.")

        return True

    return commands.check(predicate)
