# Future
from __future__ import annotations

# Standard Library
from collections.abc import Callable
from typing import TypeVar

# Packages
import discord
from discord.ext import commands

# My stuff
from utilities import custom


__all__ = (
    "has_any_permission",
)


T = TypeVar("T")


def has_any_permission(**permissions: bool) -> Callable[[T], T]:

    if invalid := set(permissions) - set(discord.Permissions.VALID_FLAGS):
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: custom.Context) -> bool:

        # permissions_for doesn't exist for certain channel types, but trust me, it's fine.
        current = dict(ctx.channel.permissions_for(ctx.author))  # type: ignore

        for permission in permissions.keys():
            if current[permission] is True:
                return True

        raise commands.CheckFailure()

    return commands.check(predicate)
