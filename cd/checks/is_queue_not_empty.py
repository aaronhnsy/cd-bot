# Future
from __future__ import annotations

# Standard Library
from collections.abc import Callable
from typing import Literal, TypeVar

# Packages
from discord.ext import commands

# My stuff
from cd import custom, exceptions


__all__ = (
    "is_queue_not_empty",
    "is_queue_history_not_empty",
)


T = TypeVar("T")


def is_queue_not_empty() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.queue._queue:
            raise exceptions.EmbedError(description="The queue is empty.")

        return True

    return commands.check(predicate)


def is_queue_history_not_empty() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.queue._history:
            raise exceptions.EmbedError(description="The queue history is empty.")

        return True

    return commands.check(predicate)
