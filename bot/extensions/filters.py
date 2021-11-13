# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
from discord.ext import commands

# My stuff
from core.bot import CD


def setup(bot: CD) -> None:
    bot.add_cog(Filters(bot))


class Filters(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: commands.Context) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Filters
