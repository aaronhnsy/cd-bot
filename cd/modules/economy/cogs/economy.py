from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord
from discord.ext import commands

from cd import custom


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "Economy",
)


class Economy(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: custom.Context) -> Literal[True]:  # pyright: reportIncompatibleMethodOverride=false

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    @commands.command(name="level", aliases=["lvl"])
    async def level(self, ctx: custom.Context, person: discord.Member | None = None) -> None:

        if not person:
            assert isinstance(ctx.author, discord.Member)
            person = ctx.author

        assert ctx.guild is not None
        url = await self.bot.manager.create_level_card(guild_id=ctx.guild.id, user_id=person.id)

        await ctx.send(url)
