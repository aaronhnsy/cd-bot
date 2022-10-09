from __future__ import annotations

import random
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from cd import enums, values
from cd.config import CONFIG


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "EconomyEvents",
)


class EconomyEvents(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    @commands.Cog.listener("on_message")
    async def handle_economy_xp_gain(self, message: discord.Message) -> None:

        if (
            (CONFIG.general.environment is not enums.Environment.PRODUCTION)
            or
            (message.guild is None)
            or
            (message.author.bot is True)
            or
            (await self.bot.redis.exists(f"{message.author.id}_{message.guild.id}_xp_gain") == 1)
        ):
            return

        xp = random.randint(10, 20)
        member_config = await self.bot.manager.get_member_config(guild_id=message.guild.id, user_id=message.author.id)

        if (
            (xp >= member_config.xp_until_next_level)
            and
            (member_config.level_up_notifications is True or member_config.guild_id == values.SKELETON_CLIQUE_GUILD_ID)
            and
            (message.channel.id != values.SKELETON_CLIQUE_COUNT_TO_INFINITY_CHANNEL_ID)
        ):
            await message.reply(f"You are now level `{member_config.level + 1}`!")

        await member_config.change_xp(enums.Operation.ADD, amount=xp)
        await self.bot.redis.setex(name=f"{message.author.id}_{message.guild.id}_xp_gain", time=60, value="")
