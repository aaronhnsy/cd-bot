# Future
from __future__ import annotations

# Standard Library
from collections.abc import Callable
from typing import TypeVar

# Packages
from discord.ext import commands

# My stuff
from utilities import custom


__all__ = (
    "is_owner",
)


T = TypeVar("T")


def is_owner() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> bool:

        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner("You do not own this bot.")

        return True

    return commands.check(predicate)
