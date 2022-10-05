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
    "SkeletonCliqueEvents",
)


class SkeletonCliqueEvents(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    _WELCOME_MESSAGES: list[str] = [
        "Welcome to trench {mention}! Enjoy your stay.",
        "Dema don't control {mention}. Welcome to the server!",
        "It looks like {member} might be one of us, welcome to **The Skeleton Clique!**",
        "{mention} just wants to say hello. Welcome to **The Skeleton Clique!**",
        "{mention} is waking up in Slowtown. Welcome to the server!",
        "Please welcome {mention} to **The Skeleton Clique!**",
        "Don't shy away! {mention}, welcome to **The Skeleton Clique!**",
    ]

    @staticmethod
    def _should_run_event(id: int) -> bool:
        return CONFIG.general.environment is enums.Environment.PRODUCTION and id == values.SKELETON_CLIQUE_GUILD_ID

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:

        if not self._should_run_event(member.guild.id):
            return

        if role := member.guild.get_role(values.SKELETON_CLIQUE_MEMBER_ROLE_ID):
            await member.add_roles(role)

        if channel := member.guild.get_channel(values.SKELETON_CLIQUE_GENERAL_CHANNEL_ID):
            assert isinstance(channel, discord.TextChannel)
            await channel.send(random.choice(self._WELCOME_MESSAGES).format(mention=member.mention))
