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
        Shows the bots prefix.
        """

        assert ctx.guild is not None

        prefix = ctx.bot._prefixes.get(ctx.guild.id, config.PREFIX)
        await ctx.send(
            embed=utils.embed(
                colour=values.MAIN,
                description=f"My prefix is `{prefix}`",
                footer="You can also mention me to use my commands!"
            )
        )

    @_prefix.command(name="set")
    async def _prefix_set(self, ctx: custom.Context, prefix: converters.Prefix) -> None:
        """
        Sets the bots prefix.

        **Arguments:**
        `prefix`: The prefix to set, surround with quotes if it contains spaces.

        **Example:**
        - `cd prefix set !` - allows you to use `!help`
        - `cd prefix set "music "` - allows you to use `music help`
        """

        assert ctx.guild is not None

        await ctx.bot._prefixes.put(ctx.guild.id, prefix)
        await ctx.send(
            embed=utils.embed(
                colour=values.MAIN,
                description=f"Set my prefix to `{prefix}`.",
            )
        )

    @_prefix.command(name="reset")
    async def _prefix_reset(self, ctx: custom.Context) -> None:
        """
        Resets the bots prefix.
        """

        assert ctx.guild is not None

        await ctx.bot._prefixes.remove(ctx.guild.id)
        await ctx.send(
            embed=utils.embed(
                colour=values.MAIN,
                description=f"Reset my prefix, it is now `{config.PREFIX}`",
            )
        )
