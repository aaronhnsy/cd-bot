# Standard Library
from collections.abc import Callable, Coroutine
from typing import Literal

# Libraries
from discord.ext import commands

# Project
from cd import custom, exceptions


__all__ = ["is_player_connected"]


def is_player_connected() -> Callable[[custom.Context], Coroutine[None, None, bool]]:
    async def predicate(ctx: custom.Context) -> Literal[True]:
        if not ctx.player or not ctx.player.is_connected():
            raise exceptions.EmbedError(description="I'm not connected to any voice channels.")
        return True
    return commands.check(predicate)
