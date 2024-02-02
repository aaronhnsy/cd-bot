# Libraries
from discord.ext import commands

# Project
from cd import custom
from ..custom import Player


__all__ = ["VoicePlayer"]


class VoicePlayer(custom.Cog):

    @commands.command(name="join", aliases=["connect"])
    async def join(self, ctx: custom.Context) -> None:
        await ctx.author.voice.channel.connect(cls=Player(link=self.bot.lavalink))

    @commands.command(name="play")
    async def play(self, ctx: custom.Context, *, search: str) -> None:
        await ctx.voice_client.update(track=(await self.bot.lavalink.search(f"ytsearch:{search}")).tracks[0])
