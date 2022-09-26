from __future__ import annotations

import random
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from cd import enums


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "EconomyEvents",
)


class EconomyEvents(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    @commands.Cog.listener("on_message")
    async def _handle_xp_gain_on_message(self, message: discord.Message) -> None:

        if message.guild is None or message.author.bot is True:
            return

        if (await self.bot.redis.exists(f"{message.author.id}_{message.guild.id}_xp_gain")) == 1:
            return

        xp = random.randint(10, 20)
        member_config = await self.bot.manager.get_member_config(guild_id=message.guild.id, user_id=message.author.id)

        if xp >= member_config.xp_until_next_level and member_config.level_up_notifications is True:
            await message.reply(f"You are now level `{member_config.level + 1}`!")

        await member_config.change_xp(enums.Operation.Add, amount=xp)
        await self.bot.redis.setex(name=f"{message.author.id}_{message.guild.id}_xp_gain", time=60, value="")
