# Future
from __future__ import annotations

# Packages
from discord.ext import commands

# My stuff
from utilities import custom, exceptions, objects


__all__ = (
    "PrefixConverter",
)


class PrefixConverter(commands.Converter[objects.FakePrefixConverter]):

    async def convert(self, ctx: custom.Context, argument: str) -> objects.FakePrefixConverter:  # pyright: reportIncompatibleMethodOverride=false

        if not (argument := (await commands.clean_content(escape_markdown=True).convert(ctx=ctx, argument=argument)).lstrip()):
            raise exceptions.EmbedError(description="You must provide a prefix.")

        if len(argument) > 50:
            raise exceptions.EmbedError(description="Your prefix must be 50 characters or less.")

        assert ctx.guild is not None
        guild_config = await ctx.bot.config.get_guild_config(ctx.guild.id)

        if argument == guild_config.prefix:
            raise exceptions.EmbedError(description="Your prefix can not be the same as the current prefix.")

        return objects.FakePrefixConverter(argument)
