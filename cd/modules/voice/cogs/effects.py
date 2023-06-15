from discord.ext import commands

from cd import custom


__all__ = ["Effects"]


class Effects(custom.Cog):

    @commands.command(name="effect")
    async def play(self, ctx: custom.Context) -> None:
        await ctx.reply("effect")
