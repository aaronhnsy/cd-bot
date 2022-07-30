from __future__ import annotations

import discord
from discord.ext import commands
from discord.ext.commands._types import Check

from cd import custom


__all__ = (
    "has_any_permission",
)


def has_any_permission(**permissions: bool) -> Check[custom.Context]:

    if invalid := set(permissions) - set(discord.Permissions.VALID_FLAGS):
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: custom.Context) -> bool:

        assert isinstance(ctx.author, discord.Member)
        current = dict(ctx.channel.permissions_for(ctx.author))

        for permission in permissions:
            if current[permission] is True:
                return True

        raise commands.CheckFailure()

    return commands.check(predicate)
