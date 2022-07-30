from __future__ import annotations

import random
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from cd import custom, enums


if TYPE_CHECKING:
    from cd.bot import SkeletonClique


__all__ = (
    "Economy",
)


class Economy(commands.Cog):

    def __init__(self, bot: SkeletonClique) -> None:
        self.bot: SkeletonClique = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        if message.guild is None or message.author.bot is True:
            return

        if (await self.bot.redis.exists(f"{message.author.id}_{message.guild.id}_xp_gain")) == 1:
            return

        member_config = await self.bot.manager.get_member_config(message.author.id, message.guild.id)
        xp = random.randint(15, 30)

        if xp >= member_config.needed_xp:
            await message.reply(f"You are now level `{member_config.level + 1}`!")

        await member_config.change_xp(enums.Operation.Add, xp)
        await self.bot.redis.setex(name=f"{message.author.id}_{message.guild.id}_xp_gain", time=1, value="")

    @commands.command(name="balance", aliases=["bal"])
    async def balance(self, ctx: custom.Context) -> None:
        member_config = await self.bot.manager.get_member_config(user_id=ctx.author.id, guild_id=ctx.guild.id)
        await ctx.send(f"You have £{member_config.money}")

    @commands.command(name="xp")
    async def xp(self, ctx: custom.Context) -> None:
        member_config = await self.bot.manager.get_member_config(user_id=ctx.author.id, guild_id=ctx.guild.id)
        await ctx.send(f"You have **{member_config.xp}** xp.")

    @commands.command(name="level", aliases=["lvl"])
    async def level(self, ctx: custom.Context) -> None:
        member_config = await self.bot.manager.get_member_config(user_id=ctx.author.id, guild_id=ctx.guild.id)
        await ctx.send(f"You are level **{member_config.level}**.")
