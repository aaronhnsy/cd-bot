from discord.ext import commands

from cd import custom


__all__ = ["Player"]


class Player(custom.Cog):

    @commands.command(name="play", aliases=["p", "pl", "ply"])
    async def play(self, ctx: custom.Context) -> None:
        await ctx.reply("play")
