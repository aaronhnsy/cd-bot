# Future
from __future__ import annotations

# Standard Library
from typing import Callable, Literal, TypeVar

# Packages
from discord.ext import commands

# My stuff
from utilities import custom, exceptions


__all__ = (
    "is_track_seekable",
)


T = TypeVar("T")


def is_track_seekable() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.current or not ctx.voice_client.current.is_seekable():
            raise exceptions.EmbedError(description="The current track is not seekable.")

        return True

    return commands.check(predicate)  # type: ignore
