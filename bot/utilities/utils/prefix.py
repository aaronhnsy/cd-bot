from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from discord import Message
    from bot.core.bot import CD

__all__ = (
    "get_prefixes",
)

async def get_prefixes(bot: CD, message: Message) -> list[str]:
    if message.guild:
        custom_prefixes: list[str] = bot._prefixes.get(message.guild.id)
        return commands.when_mentioned_or(*custom_prefixes)(bot, message)
    return commands.when_mentioned_or(*bot.config.PREFIX)(bot, message)
