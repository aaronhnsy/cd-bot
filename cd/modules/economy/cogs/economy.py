from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Literal

import discord
from discord.ext import commands

from cd import custom


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "Economy",
)


_MEMBER_DEFAULT: Callable[[custom.Context], discord.User | discord.Member] = lambda ctx: ctx.author
_MEMBER_CONVERTER = commands.parameter(default=_MEMBER_DEFAULT)


class Economy(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: custom.Context) -> Literal[True]:  # pyright: reportIncompatibleMethodOverride=false

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    @commands.hybrid_command(name="level", aliases=["lvl"])
    async def level(self, ctx: custom.Context, person: discord.Member = _MEMBER_CONVERTER) -> None:
        """
        Shows yours, or another member's level card.
        """

        assert ctx.guild is not None

        async with ctx.typing():
            url = await self.bot.manager.create_level_card(guild_id=ctx.guild.id, user_id=person.id)
            await ctx.send(url)
