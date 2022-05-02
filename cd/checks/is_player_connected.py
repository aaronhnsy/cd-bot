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
    "is_player_connected",
)


T = TypeVar("T")


def is_player_connected() -> Check[custom.Context]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            raise exceptions.EmbedError(description="I'm not connected to any voice channels.")

        return True

    return commands.check(predicate)
