# Future
from __future__ import annotations

# Standard Library
from collections.abc import Callable
from typing import TypeVar

# Packages
from discord.ext import commands

# My stuff
from cd import custom


__all__ = (
    "is_guild_owner",
)


T = TypeVar("T")


def is_guild_owner() -> Callable[[T], T]:

    def predicate(ctx: custom.Context) -> bool:
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id

    return commands.check(predicate)
