# Future
from __future__ import annotations

# Standard Library
from typing import Callable, Literal, TypeVar

# Packages
from discord.ext import commands

# My stuff
from utilities import custom, exceptions


__all__ = (
    "is_player_connected",
)


T = TypeVar("T")


def is_player_connected() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            raise exceptions.EmbedError(description="I'm not connected to any voice channels.")

        return True

    return commands.check(predicate)  # type: ignore
