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
    "is_track_seekable",
)


T = TypeVar("T")


def is_track_seekable() -> Check[custom.Context]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.player or not ctx.player.current or not ctx.player.current.is_seekable():
            raise exceptions.EmbedError(description="The current track is not seekable.")

        return True

    return commands.check(predicate)
