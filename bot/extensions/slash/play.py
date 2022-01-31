# Future
from __future__ import annotations

# Packages
import slate
import slate.obsidian

# My stuff
from core.bot import CD
from utilities import custom, exceptions, slash


def setup(bot: CD) -> None:
    bot.add_cog(SlashPlay(bot))


class SlashPlay(slash.ApplicationCog):

    @staticmethod
    async def _ensure_connected(ctx: slash.ApplicationContext) -> None:

        author_voice_channel = ctx.author.voice and ctx.author.voice.channel
        bot_voice_channel = ctx.voice_client and ctx.voice_client.voice_channel

        # If the user and the bot are in the same
        # channel, return because we don't need to
        # do anything.
        if author_voice_channel and bot_voice_channel and author_voice_channel == bot_voice_channel:
            return

        # If the user is not in a voice channel but
        # the bot is OR they are both in a voice
        # channel but not the same one, tell the
        # user to join the bots channel.
        if not author_voice_channel and bot_voice_channel or author_voice_channel and bot_voice_channel:
            raise exceptions.EmbedError(description=f"You must be connected to {bot_voice_channel.mention} to use this command.")

        # If the user is not in a voice channel, tell
        # them to join one.
        if not author_voice_channel:
            raise exceptions.EmbedError(description="You must be connected to a voice channel to use this command.")

        # Join the users voice channel.
        await author_voice_channel.connect(cls=custom.Player)  # type: ignore
        ctx.voice_client.text_channel = ctx.channel  # type: ignore

    # Play

    @slash.slash_command(name="play", guild_id=240958773122957312)
    async def play(self, ctx: slash.ApplicationContext, next: bool = False, now: bool = False, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.obsidian.Source.YOUTUBE, ctx=ctx, play_next=next, play_now=now)

    @slash.slash_command(name="search", guild_id=240958773122957312)
    async def search(self, ctx: slash.ApplicationContext, next: bool = False, now: bool = False, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.obsidian.Source.YOUTUBE, ctx=ctx, search_select=True, play_next=next, play_now=now)

    # Youtube music

    @slash.slash_command(name="youtube-music", guild_id=240958773122957312)
    async def youtube_music(self, ctx: slash.ApplicationContext, next: bool = False, now: bool = False, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.obsidian.Source.YOUTUBE_MUSIC, ctx=ctx, play_next=next, play_now=now)

    @slash.slash_command(name="youtube-music-search", guild_id=240958773122957312)
    async def youtube_music_search(self, ctx: slash.ApplicationContext, next: bool = False, now: bool = False, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.obsidian.Source.YOUTUBE_MUSIC, ctx=ctx, search_select=True, play_next=next, play_now=now)

    # Soundcloud

    @slash.slash_command(name="soundcloud", guild_id=240958773122957312)
    async def soundcloud(self, ctx: slash.ApplicationContext, next: bool = False, now: bool = False, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.obsidian.Source.SOUNDCLOUD, ctx=ctx, play_next=next, play_now=now)

    @slash.slash_command(name="soundcloud-search", guild_id=240958773122957312)
    async def soundcloud_search(self, ctx: slash.ApplicationContext, next: bool = False, now: bool = False, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.obsidian.Source.SOUNDCLOUD, ctx=ctx, search_select=True, play_next=next, play_now=now)

    # Local

    @slash.slash_command(name="local", guild_id=240958773122957312)
    async def local(self, ctx: slash.ApplicationContext, next: bool = False, now: bool = False, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.obsidian.Source.LOCAL, ctx=ctx, play_next=next, play_now=now)

    # HTTP

    @slash.slash_command(name="http", guild_id=240958773122957312)
    async def http(self, ctx: slash.ApplicationContext, next: bool = False, now: bool = False, *, query: str) -> None:

        await self._ensure_connected(ctx)

        assert ctx.voice_client is not None
        await ctx.voice_client.queue_search(query, source=slate.obsidian.Source.HTTP, ctx=ctx, play_next=next, play_now=now)
