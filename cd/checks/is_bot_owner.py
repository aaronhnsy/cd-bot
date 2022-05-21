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
    "is_bot_owner",
)


def is_bot_owner() -> Check[custom.Context]:

    async def predicate(ctx: custom.Context) -> bool:

        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner("You do not own this bot.")

        return True

    return commands.check(predicate)
