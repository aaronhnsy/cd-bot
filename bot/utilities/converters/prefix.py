from discord.ext import commands
from discord import utils

from utilities import custom

__all__ = (
    "Prefix",
)

class Prefix(commands.Converter):
    async def convert(self, ctx: custom.Context, argument: str) -> str:  # type: ignore - some unusual subclassing error due to Generic Context

        # assume Guild exists due to prior locks
        assert ctx.guild is not None

        prefixes: list[str] = ctx.bot._prefixes.get(ctx.guild.id)

        if argument in prefixes:
            raise commands.BadArgument("This is already a prefix here!")

        return utils.escape_mentions(argument)
