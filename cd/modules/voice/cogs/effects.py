from discord.ext import commands

from cd import custom


__all__ = ["VoiceEffects"]


class VoiceEffects(custom.Cog, name="Voice Effects"):
    emoji = "💥"
    description = "Add effects and filters to the music."

    @commands.command(name="effect")
    async def effect(self, ctx: custom.Context) -> None:
        await ctx.reply("effect")
