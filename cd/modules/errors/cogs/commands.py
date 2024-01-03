# Libraries
from discord.ext import commands

# Project
from cd import custom


__all__ = ["ErrorsCommands"]


class ErrorsCommands(custom.Cog, name="Errors"):

    @commands.command()
    async def test(self, ctx: custom.Context) -> None:
        raise ValueError("This is a test error.")
