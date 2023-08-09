# Libraries
import discord

# Project
from cd import custom


__all__ = ["MiscEvents"]


class MiscEvents(custom.Cog):

    @custom.Cog.listener("on_message_edit")
    async def reinvoke_command_on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.content == after.content:
            return
        await self.bot.process_commands(after)
