# Future
from __future__ import annotations

# Standard Library
from collections.abc import Callable
from typing import Literal, TypeVar

# Packages
from discord.ext import commands

# My stuff
from utilities import custom, exceptions


__all__ = (
    "is_player_playing",
)


T = TypeVar("T")


def is_player_playing() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.is_playing():
            raise exceptions.EmbedError(description="There are no tracks playing.")

        return True

    return commands.check(predicate)
