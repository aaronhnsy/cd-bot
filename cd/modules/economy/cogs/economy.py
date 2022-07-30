from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

from cd import custom


if TYPE_CHECKING:
    from cd.bot import SkeletonClique


__all__ = (
    "Economy",
)


class Economy(commands.Cog):

    def __init__(self, bot: SkeletonClique) -> None:
        self.bot: SkeletonClique = bot

    @commands.command(name="balance", aliases=["bal"])
    async def balance(self, ctx: custom.Context) -> None:

        member_config = await self.bot.manager.get_member_config(user_id=ctx.author.id, guild_id=ctx.guild.id)
        await ctx.send(f"You have £{member_config.money}")
