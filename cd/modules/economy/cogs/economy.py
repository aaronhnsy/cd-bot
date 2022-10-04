from __future__ import annotations

import functools
from collections.abc import Callable
from typing import TYPE_CHECKING, Literal

import discord
from discord.ext import commands

from cd import custom, paginators


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

    @commands.hybrid_command(name="level", aliases=["lvl", "rank"])
    async def level(self, ctx: custom.Context, person: discord.Member = _MEMBER_CONVERTER) -> None:
        """
        Shows yours, or another member's level card.
        """

        assert ctx.guild is not None

        async with ctx.typing():
            member_config = await self.bot.manager.get_member_config(guild_id=ctx.guild.id, user_id=person.id)
            await ctx.send(await member_config.create_level_card())

    @commands.hybrid_command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx: custom.Context) -> None:
        """
        Displays the leaderboard for ranks, xp and levels.
        """

        assert ctx.guild is not None

        count: dict[Literal["count"], int] = await self.bot.db.fetchrow(
            "SELECT count(*) FROM members WHERE guild_id = $1",
            ctx.guild.id
        )
        pages = (count["count"] // 10) + 1

        guild_config = await self.bot.manager.get_guild_config(ctx.guild.id)

        await paginators.FilePaginator(
            ctx=ctx,
            entries=[functools.partial(guild_config.create_leaderboard, page=page) for page in range(pages)]
        ).start()
