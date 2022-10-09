from __future__ import annotations

import random
from typing import TYPE_CHECKING, Final

import discord
from discord.ext import commands

from cd import enums, values, utilities
from cd.config import CONFIG


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "SkeletonCliqueEvents",
)


class SkeletonCliqueEvents(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot
        self.last_count_to_infinity_number: int = utilities.MISSING

    WELCOME_MESSAGES: Final[list[str]] = [
        "Welcome to trench {mention}! Enjoy your stay.",
        "Dema don't control {mention}. Welcome to the server!",
        "It looks like {member} might be one of us, welcome to **The Skeleton Clique!**",
        "{mention} just wants to say hello. Welcome to **The Skeleton Clique!**",
        "{mention} is waking up in Slowtown. Welcome to the server!",
        "Please welcome {mention} to **The Skeleton Clique!**",
        "Don't shy away! {mention}, welcome to **The Skeleton Clique!**",
    ]

    @commands.Cog.listener("on_member_join")
    async def handle_skeleton_clique_welcome_messages(self, member: discord.Member) -> None:

        if (
            (CONFIG.general.environment is not enums.Environment.PRODUCTION)
            or
            (member.guild.id != values.SKELETON_CLIQUE_GUILD_ID)
            or
            (member.bot is True)
        ):
            return

        if role := member.guild.get_role(values.SKELETON_CLIQUE_MEMBER_ROLE_ID):
            await member.add_roles(role)

        if channel := member.guild.get_channel(values.SKELETON_CLIQUE_GENERAL_CHANNEL_ID):
            assert isinstance(channel, discord.TextChannel)
            await channel.send(random.choice(self.WELCOME_MESSAGES).format(mention=member.mention))

    @commands.Cog.listener("on_message")
    async def handle_skeleton_clique_count_to_infinity_channel(self, message: discord.Message) -> None:

        if (
            (CONFIG.general.environment is not enums.Environment.PRODUCTION)
            or
            (message.channel.id != values.SKELETON_CLIQUE_COUNT_TO_INFINITY_CHANNEL_ID)
            or
            (message.author.bot is True)
        ):
            return

        try:
            number = int(message.content)
        except ValueError:
            await message.reply(
                "That wasn't a valid number!",
                allowed_mentions=discord.AllowedMentions.all(),
                delete_after=5
            )
            await message.delete(delay=5)
            return

        if self.last_count_to_infinity_number is utilities.MISSING:
            try:
                assert isinstance(message.channel, discord.TextChannel)
                messages = [msg async for msg in message.channel.history(limit=25) if msg.content.isdecimal()]
                self.last_count_to_infinity_number = int(messages[1].content)
            except (discord.HTTPException, discord.Forbidden, IndexError, ValueError):
                return

        if (number - self.last_count_to_infinity_number) != 1:
            await message.reply(
                f"The next number should be **{self.last_count_to_infinity_number + 1}**!",
                allowed_mentions=discord.AllowedMentions.all(),
                delete_after=5
            )
            await message.delete(delay=5)
            return

        self.last_count_to_infinity_number = number
