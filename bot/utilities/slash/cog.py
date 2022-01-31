# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any

# Packages
import discord
import discord.types.interactions
from discord.ext import commands

# My stuff
from utilities.slash.context import ApplicationContext


if TYPE_CHECKING:
    # My stuff
    from core.bot import CD


__all__ = (
    "ApplicationCog",
)


class ApplicationCog(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    @commands.Cog.listener("on_interaction")
    async def _internal_interaction_handler(self, interaction: discord.Interaction) -> None:

        if interaction.type is not discord.InteractionType.application_command:
            return

        if not (command := self.bot.application_commands.get(interaction.data["name"])):
            return

        params: dict[str, Any] = command._build_arguments(interaction, self.bot._connection)

        ctx = ApplicationContext(interaction, self.bot, command)
        try:
            await command.invoke(ctx, **params)
        except Exception as error:
            self.bot.dispatch("command_error", ctx, error)
