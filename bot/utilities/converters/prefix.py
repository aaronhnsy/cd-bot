# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Packages
from discord.ext import commands

# My stuff
from core import values
from utilities import exceptions, objects


if TYPE_CHECKING:
    # My stuff
    from core.bot import CD


__all__ = (
    "PrefixConverter",
)


class PrefixConverter(commands.Converter[objects.FakePrefixConverter]):

    async def convert(self, ctx: commands.Context[CD], argument: str) -> objects.FakePrefixConverter:

        if not (argument := (await commands.clean_content(escape_markdown=True).convert(ctx=ctx, argument=argument)).lstrip()):
            raise exceptions.EmbedError(description="You must provide a prefix.")

        if len(argument) > 50:
            raise exceptions.EmbedError(description="Your prefix must be 50 characters or less.")

        assert ctx.guild is not None
        guild_config = await ctx.bot.config.get_guild_config(ctx.guild.id)

        if argument == guild_config.prefix:
            raise exceptions.EmbedError(description="Your prefix can not be the same as the current prefix.")

        return objects.FakePrefixConverter(argument)
