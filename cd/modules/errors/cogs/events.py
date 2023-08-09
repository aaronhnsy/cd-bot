# Libraries
from discord.ext import commands

# Project
from cd import custom, utilities, values
from cd.modules.errors.handlers import HANDLERS, command_not_found, original


__all__ = ["ErrorsEvents"]


class ErrorsEvents(custom.Cog):

    @custom.Cog.listener("on_command_error")
    async def on_command_error(self, ctx: custom.Context, error: commands.CommandError) -> None:
        if type(error) in HANDLERS:
            response = HANDLERS[type(error)](error, ctx)
            await ctx.reply(
                embed=utilities.embed(
                    colour=values.ERROR_COLOUR,
                    description=response.description,
                    footer=response.footer,
                )
            )
        elif isinstance(error, commands.ConversionError | commands.CommandInvokeError | commands.HybridCommandError):
            await original(error.original, ctx)
        elif isinstance(error, commands.CommandNotFound):
            await command_not_found(error, ctx)
        else:
            await original(error, ctx)
