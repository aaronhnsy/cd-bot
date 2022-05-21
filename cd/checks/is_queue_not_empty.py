# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Literal

# Packages
from discord.ext import commands

# Local
from cd import custom, exceptions


if TYPE_CHECKING:
    # Packages
    from discord.ext.commands._types import Check


__all__ = (
    "is_queue_not_empty",
    "is_queue_history_not_empty",
)


def is_queue_not_empty() -> Check[custom.Context]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.player or not ctx.player.queue.items:
            raise exceptions.EmbedError(description="The queue is empty.")

        return True

    return commands.check(predicate)


def is_queue_history_not_empty() -> Check[custom.Context]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.player or not ctx.player.queue.history:
            raise exceptions.EmbedError(description="The queue history is empty.")

        return True

    return commands.check(predicate)
