from __future__ import annotations

from typing import Literal

from discord.ext import commands
from discord.ext.commands._types import Check

from cd import custom, exceptions


__all__ = (
    "is_queue_not_empty",
    "is_queue_history_not_empty",
)


def is_queue_not_empty() -> Check[custom.Context]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.player or ctx.player.queue.is_empty():
            raise exceptions.EmbedError(description="The queue is empty.")

        return True

    return commands.check(predicate)


def is_queue_history_not_empty() -> Check[custom.Context]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.player or ctx.player.queue.is_history_empty():
            raise exceptions.EmbedError(description="The queue history is empty.")

        return True

    return commands.check(predicate)
