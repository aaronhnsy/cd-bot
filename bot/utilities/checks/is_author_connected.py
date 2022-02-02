# Future
from __future__ import annotations

# Standard Library
from typing import Callable, Literal, TypeVar

# Packages
import discord
from discord.ext import commands

# My stuff
from utilities import custom, exceptions


__all__ = (
    "is_author_connected",
)


T = TypeVar("T")


def is_author_connected() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        assert isinstance(ctx.author, discord.Member)

        author_channel = ctx.author.voice and ctx.author.voice.channel
        voice_client_channel = ctx.voice_client and ctx.voice_client.voice_channel

        if voice_client_channel != author_channel:
            raise exceptions.EmbedError(
                description=f"you must be connected to {getattr(voice_client_channel, 'mention', None)} to use this command.",
            )

        return True

    return commands.check(predicate)  # type: ignore
