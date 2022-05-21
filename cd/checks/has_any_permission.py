# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Packages
import discord
from discord.ext import commands

# Local
from cd import custom


if TYPE_CHECKING:
    # Packages
    from discord.ext.commands._types import Check


__all__ = (
    "has_any_permission",
)


def has_any_permission(**permissions: bool) -> Check[custom.Context]:

    if invalid := set(permissions) - set(discord.Permissions.VALID_FLAGS):
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: custom.Context) -> bool:

        assert isinstance(ctx.author, discord.Member)
        current = dict(ctx.channel.permissions_for(ctx.author))

        for permission in permissions.keys():
            if current[permission] is True:
                return True

        raise commands.CheckFailure()

    return commands.check(predicate)
