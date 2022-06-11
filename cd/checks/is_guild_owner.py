# Future
from __future__ import annotations

# Packages
from discord.ext import commands
from discord.ext.commands._types import Check

# Local
from cd import custom


__all__ = (
    "is_guild_owner",
)


def is_guild_owner() -> Check[custom.Context]:

    def predicate(ctx: custom.Context) -> bool:
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id

    return commands.check(predicate)
