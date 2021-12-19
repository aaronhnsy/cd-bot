# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
from discord.ext import commands

# My stuff
from core import config, values
from core.bot import CD
from utilities import converters, custom, utils


def setup(bot: CD) -> None:
    bot.add_cog(Settings(bot))


class Settings(commands.Cog):
    """
    Change the bots settings.
    """

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: commands.Context[CD]) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    #

    @commands.group(name="prefix", invoke_without_command=True)
    async def _prefix(self, ctx: custom.Context) -> None:
        """
        See the current prefix for this server.
        """

        assert ctx.guild is not None

        embed = utils.embed(
            colour=values.MAIN,
            description=f"My prefix is `{ctx.bot._prefixes.get(ctx.guild.id, config.PREFIX)}`",
            footer="You can also mention me to use my commands!"
        )
        await ctx.send(embed=embed)

    @_prefix.command(name="set")
    async def _prefix_set(self, ctx: custom.Context, prefix: converters.Prefix) -> None:
        """
        Set the prefix for this server.
        """

        assert ctx.guild is not None

        await ctx.bot._prefixes.put(ctx.guild.id, prefix)

        embed = utils.embed(
            colour=values.MAIN,
            description=f"Set my prefix for this server to `{prefix}`.",
        )
        await ctx.send(embed=embed)
