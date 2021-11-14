# Future
from __future__ import annotations

# Packages
import discord
from discord.ext import commands

# My stuff
from core import values
from utilities import custom


__all__ = (
    "bot",
)


async def bot(ctx: custom.Context) -> bool:

    assert not isinstance(ctx.channel, discord.PartialMessageable)

    current = dict(ctx.channel.permissions_for(ctx.me))  # type: ignore
    needed = {permission: value for permission, value in values.PERMISSIONS if value is True}

    if missing := [permission for permission, value in needed.items() if current[permission] != value]:
        raise commands.BotMissingPermissions(missing)

    return True
