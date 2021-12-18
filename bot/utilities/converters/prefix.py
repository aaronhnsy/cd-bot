# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Packages
from discord.ext import commands

# My stuff
from core import config, values
from utilities import exceptions


if TYPE_CHECKING:
    # My stuff
    from core.bot import CD


__all__ = (
    "Prefix",
)


class Prefix(commands.Converter[str]):

    async def convert(self, ctx: commands.Context[CD], argument: str) -> str:

        if not (argument := (await commands.clean_content(escape_markdown=True).convert(ctx=ctx, argument=argument)).lstrip()):
            raise exceptions.EmbedError(
                colour=values.RED,
                description="You must provide a prefix."
            )

        if len(argument) > 50:
            raise exceptions.EmbedError(
                colour=values.RED,
                description="Your prefix must be 50 characters or less."
            )

        assert ctx.guild is not None

        prefix: str = ctx.bot._prefixes.get(ctx.guild.id, config.PREFIX)
        if argument == prefix:
            raise exceptions.EmbedError(
                colour=values.RED,
                description="Your prefix can not be the same as the current prefix."
            )

        return argument
