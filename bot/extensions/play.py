# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import discord
import slate
import slate.obsidian
from discord.ext import commands

# My stuff
from core.bot import CD
from utilities import custom, exceptions


def setup(bot: CD) -> None:
    bot.add_cog(Play(bot))


class Play(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: commands.Context) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    @staticmethod
    async def _check_playable(ctx: custom.Context) -> None:

        assert isinstance(ctx.author, discord.Member)

        author_channel = ctx.author.voice and ctx.author.voice.channel
        bot_channel = ctx.voice_client and ctx.voice_client.voice_channel

        if not author_channel:
            if bot_channel:
                raise exceptions.EmbedError(description=f"You must be connected to {bot_channel.mention} to use this command.")
            raise exceptions.EmbedError(description="You must be connected to a voice channel to use this command.")

        if bot_channel:
            if bot_channel == author_channel:
                return
            raise exceptions.EmbedError(description=f"You must be connected to {bot_channel.mention} to use this command.")

        await author_channel.connect(cls=custom.Player)  # type: ignore
        ctx.voice_client._text_channel = ctx.channel  # type: ignore

    # Play

    @commands.command(name="play")
    async def play(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.YOUTUBE)

    @commands.command(name="play-now")
    async def play_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.YOUTUBE, now=True)

    @commands.command(name="play-next")
    async def play_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.YOUTUBE, next=True)

    # Youtube

    @commands.command(name="youtube")
    async def youtube(self, ctx: custom.Context, *, query: str) -> None:
        await self.play(ctx, query=query)

    @commands.command(name="youtube-now")
    async def youtube_now(self, ctx: custom.Context, *, query: str) -> None:
        await self.play_now(ctx, query=query)

    @commands.command(name="youtube-next")
    async def youtube_next(self, ctx: custom.Context, *, query: str) -> None:
        await self.play_next(ctx, query=query)

    # Youtube music

    @commands.command(name="youtube-music")
    async def youtube_music(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.YOUTUBE_MUSIC)

    @commands.command(name="youtube-music-now")
    async def youtube_music_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.YOUTUBE_MUSIC, now=True)

    @commands.command(name="youtube-music-next")
    async def youtube_music_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.YOUTUBE_MUSIC, next=True)

    # Soundcloud

    @commands.command(name="soundcloud")
    async def soundcloud(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.SOUNDCLOUD)

    @commands.command(name="soundcloud-now")
    async def soundcloud_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.SOUNDCLOUD, now=True)

    @commands.command(name="soundcloud-next")
    async def soundcloud_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.SOUNDCLOUD, next=True)

    # Local

    @commands.command(name="local", hidden=True)
    async def local(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.LOCAL)

    @commands.command(name="local-now", hidden=True)
    async def local_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.LOCAL, now=True)

    @commands.command(name="local-next", hidden=True)
    async def local_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.LOCAL, next=True)

    # HTTP

    @commands.command(name="http", hidden=True)
    async def http(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.NONE)

    @commands.command(name="http-now", hidden=True)
    async def http_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.NONE, now=True)

    @commands.command(name="http-next", hidden=True)
    async def http_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._check_playable(ctx)
        assert ctx.voice_client is not None

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.NONE, next=True)
