# Libraries
from discord.ext import commands

# Project
from cd import custom


__all__ = ["VoicePlayer"]


class VoicePlayer(custom.Cog):

    @commands.command(name="play", aliases=["p", "pl", "ply"])
    async def play(self, ctx: custom.Context) -> None:
        await ctx.reply("play")
