import discord

from cd import custom


__all__ = ["Meta"]


class Meta(custom.Cog, name="Meta"):
    emoji = "🔧"
    description = "Owner-only commands for debugging and using the bot."

    @custom.Cog.listener("on_message_edit")
    async def reinvoke_command_on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.content == after.content:
            return
        await self.bot.process_commands(after)

