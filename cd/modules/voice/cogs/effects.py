# Libraries
from discord.ext import commands

# Project
from cd import custom


__all__ = ["VoiceEffects"]


class VoiceEffects(custom.Cog):

    @commands.command(name="effect")
    async def play(self, ctx: custom.Context) -> None:
        await ctx.reply("effect")
