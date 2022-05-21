# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Packages
from discord.ext import commands

# Local
from cd import custom


if TYPE_CHECKING:
    # Packages
    from discord.ext.commands._types import Check


__all__ = (
    "is_guild_owner",
)


def is_guild_owner() -> Check[custom.Context]:

    def predicate(ctx: custom.Context) -> bool:
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id

    return commands.check(predicate)
