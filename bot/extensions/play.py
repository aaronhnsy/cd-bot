# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import discord
import slate
from discord.ext import commands

# My stuff
from core.bot import CD
from utilities import custom, exceptions


def setup(bot: CD) -> None:
    bot.add_cog(Play(bot))


class Play(commands.Cog):
    """
    Various platform-specific play commands.
    """

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: commands.Context[CD]) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    @staticmethod
    async def _ensure_connected(ctx: custom.Context) -> None:

        assert isinstance(ctx.author, discord.Member)

        author_voice_channel = ctx.author.voice and ctx.author.voice.channel
        bot_voice_channel = ctx.voice_client and ctx.voice_client.voice_channel

        if (author_voice_channel and bot_voice_channel) and (author_voice_channel == bot_voice_channel):
            return

        if (not author_voice_channel and bot_voice_channel) or (author_voice_channel and bot_voice_channel):
            raise exceptions.EmbedError(description=f"You must be connected to {bot_voice_channel.mention} to use this command.")

        if not author_voice_channel:
            raise exceptions.EmbedError(description="You must be connected to a voice channel to use this command.")

        await author_voice_channel.connect(cls=custom.Player(text_channel=ctx.channel))  # type: ignore

    # Play

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: custom.Context, *, query: str) -> None:
        """
        Searches for and adds a track to the queue.

        **Arguments:**
        `query`: The track to search for. Can be a URL or search query.

        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE, ctx=ctx)

    @commands.command(name="play-next", aliases=["play_next", "playnext", "pne"])
    async def play_next(self, ctx: custom.Context, *, query: str) -> None:
        """
        Searches for and adds a track to the start of the queue.

        **Arguments:**
        `query`: The track to search for. Can be a URL or search query.

        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE, ctx=ctx, play_next=True)

    @commands.command(name="play-now", aliases=["play_now", "playnow", "pno"])
    async def play_now(self, ctx: custom.Context, *, query: str) -> None:
        """
        Searches for and plays a track immediately.

        **Arguments:**
        `query`: The track to search for. Can be a URL or search query.

        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE, ctx=ctx, play_now=True)

    # Search

    @commands.command(name="search", aliases=["s"])
    async def search(self, ctx: custom.Context, *, query: str) -> None:
        """
        Allows you to select which tracks to add to the queue.

        **Arguments:**
        `query`: The track to search for. Can be a URL or search query.

        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE, ctx=ctx, search_select=True)

    @commands.command(name="search-next", aliases=["search_next", "searchnext", "sne"], hidden=True)
    async def search_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE, ctx=ctx, search_select=True, play_next=True)

    @commands.command(name="search-now", aliases=["search_now", "searchnow", "sno"], hidden=True)
    async def search_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE, ctx=ctx, search_select=True, play_now=True)

    # Youtube

    @commands.command(name="youtube", aliases=["yt"])
    async def youtube(self, ctx: custom.Context, *, query: str) -> None:
        """
        Searches for tracks from YouTube to add to the queue.

        **Arguments:**
        `query`: The track to search for. Can be a URL or search query.
        """
        await self.play(ctx, query=query)

    @commands.command(name="youtube-next", aliases=["youtube_next", "youtubenext", "ytne"], hidden=True)
    async def youtube_next(self, ctx: custom.Context, *, query: str) -> None:
        await self.play_next(ctx, query=query)

    @commands.command(name="youtube-now", aliases=["youtube_now", "youtubenow", "ytno"], hidden=True)
    async def youtube_now(self, ctx: custom.Context, *, query: str) -> None:
        await self.play_now(ctx, query=query)

    # YouTube search

    @commands.command(name="youtube-search", aliases=["youtube_search", "youtubesearch", "yts"])
    async def youtube_search(self, ctx: custom.Context, *, query: str) -> None:
        """
        Allows you to select which tracks from YouTube to add to the queue.

        **Arguments:**
        `query`: The track to search for. Can be a URL or search query.
        """
        await self.search(ctx, query=query)

    @commands.command(name="youtube-search-next", aliases=["youtube_search_next", "youtubesearchnext", "ytsne"], hidden=True)
    async def youtube_search_next(self, ctx: custom.Context, *, query: str) -> None:
        await self.search_next(ctx, query=query)

    @commands.command(name="youtube-search-now", aliases=["youtube_search_now", "youtubesearchnow", "ytsno"], hidden=True)
    async def youtube_search_now(self, ctx: custom.Context, *, query: str) -> None:
        await self.search_now(ctx, query=query)

    # YouTube Music

    @commands.command(name="youtube-music", aliases=["youtube_music", "youtubemusic", "ytm"])
    async def youtube_music(self, ctx: custom.Context, *, query: str) -> None:
        """
        Searches for tracks from YouTube Music to add to the queue.

        **Arguments:**
        `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx)

    @commands.command(name="youtube-music-next", aliases=["youtube_music_next", "youtubemusicnext", "ytmne"], hidden=True)
    async def youtube_music_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, play_next=True)

    @commands.command(name="youtube-music-now", aliases=["youtube_music_now", "youtubemusicnow", "ytmno"], hidden=True)
    async def youtube_music_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, play_now=True)

    # YouTube Music search

    @commands.command(name="youtube-music-search", aliases=["youtube_music_search", "youtubemusicsearch", "ytms"])
    async def youtube_music_search(self, ctx: custom.Context, *, query: str) -> None:
        """
        Allows you to select which tracks from YouTube Music to add to the queue.

        **Arguments:**
        `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, search_select=True)

    @commands.command(name="youtube-music-search-next", aliases=["youtube_music_search_next", "youtubemusicsearchnext", "ytmsne"], hidden=True)
    async def youtube_music_search_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, search_select=True, play_next=True)

    @commands.command(name="youtube-music-search-now", aliases=["youtube_music_search_now", "youtubemusicsearchnow", "ytmsno"], hidden=True)
    async def youtube_music_search_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, search_select=True, play_now=True)

    # Soundcloud

    @commands.command(name="soundcloud", aliases=["sc"])
    async def soundcloud(self, ctx: custom.Context, *, query: str) -> None:
        """
        Searches for tracks from Soundcloud to add to the queue.

        **Arguments:**
        `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.SOUNDCLOUD, ctx=ctx)

    @commands.command(name="soundcloud-next", aliases=["soundcloud_next", "soundcloudnext", "scne"], hidden=True)
    async def soundcloud_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.SOUNDCLOUD, ctx=ctx, play_next=True)

    @commands.command(name="soundcloud-now", aliases=["soundcloud_now", "soundcloudnow", "scno"], hidden=True)
    async def soundcloud_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.SOUNDCLOUD, ctx=ctx, play_now=True)

    # Soundcloud search

    @commands.command(name="soundcloud-search", aliases=["soundcloud_search", "soundcloudsearch", "scs"])
    async def soundcloud_search(self, ctx: custom.Context, *, query: str) -> None:
        """
        Allows you to select which tracks from Soundcloud to add to the queue.

        **Arguments:**
        `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.SOUNDCLOUD, ctx=ctx, search_select=True)

    @commands.command(name="soundcloud-search-next", aliases=["soundcloud_search_next", "soundcloudsearchnext", "scsne"], hidden=True)
    async def soundcloud_search_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.SOUNDCLOUD, ctx=ctx, search_select=True, play_next=True)

    @commands.command(name="soundcloud-search-now", aliases=["soundcloud_search_now", "soundcloudsearchnow", "scsno"], hidden=True)
    async def soundcloud_search_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.SOUNDCLOUD, ctx=ctx, search_select=True, play_now=True)

    # Local

    @commands.command(name="local", aliases=["l"], hidden=True)
    @commands.is_owner()
    async def local(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.LOCAL, ctx=ctx)

    @commands.command(name="local-next", aliases=["local_next", "localnext", "lne"], hidden=True)
    @commands.is_owner()
    async def local_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.LOCAL, ctx=ctx, play_next=True)

    @commands.command(name="local-now", aliases=["local_now", "localnow", "lno"], hidden=True)
    @commands.is_owner()
    async def local_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.LOCAL, ctx=ctx, play_now=True)

    # HTTP

    @commands.command(name="http", aliases=["h"], hidden=True)
    @commands.is_owner()
    async def http(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.NONE, ctx=ctx)

    @commands.command(name="http-next", aliases=["http_next", "httpnext", "hne"], hidden=True)
    @commands.is_owner()
    async def http_next(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.NONE, ctx=ctx, play_next=True)

    @commands.command(name="http-now", aliases=["http_now", "httpnow", "hno"], hidden=True)
    @commands.is_owner()
    async def http_now(self, ctx: custom.Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.Source.NONE, ctx=ctx, play_now=True)
