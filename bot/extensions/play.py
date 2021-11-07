# Future
from __future__ import annotations

# Packages
import discord
import slate
import slate.obsidian
from discord.ext import commands

# My stuff
from core import values
from core.bot import CD
from utilities import checks, custom, exceptions, utils


def setup(bot: CD) -> None:
    bot.add_cog(Play(bot))


class Play(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    #

    @commands.command(name="join", aliases=["summon", "connect"])
    async def join(self, ctx: custom.Context) -> None:
        """
        Joins the bot to your voice channel.
        """

        assert isinstance(ctx.author, discord.Member)

        if ctx.voice_client and ctx.voice_client.is_connected():
            raise exceptions.EmbedError(
                description=f"I am already connected to {ctx.voice_client.voice_channel.mention}.",
            )

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise exceptions.EmbedError(
                description="You must be connected to a voice channel to use this command.",
            )

        await ctx.author.voice.channel.connect(cls=custom.Player)  # type: ignore
        assert ctx.voice_client is not None

        ctx.voice_client._text_channel = ctx.channel  # type: ignore
        assert ctx.voice_client.text_channel is not None

        await ctx.send(embed=utils.embed(colour=values.GREEN, description=f"Joined {ctx.voice_client.voice_channel.mention}."))

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: custom.Context, *, query: str) -> None:
        """
        Queues tracks with the given name or url.

        **query**: The query to search for tracks with.

        **Flags:**
        **--music**: Searches [YouTube music](https://music.youtube.com/) for results.
        **--soundcloud**: Searches [soundcloud](https://soundcloud.com/) for results.
        **--next**: Puts the track that is found at the start of the queue.
        **--now**: Skips the current track and plays the track that is found.

        **Usage:**
        `l-play If I Can't Have You by Shawn Mendes --now`
        `l-play Señorita by Shawn Mendes --next`
        `l-play Lost In Japan by Shawn Mendes --soundcloud --now`
        """

        if (
            ctx.voice_client is None or ctx.voice_client.is_connected() is False
        ) and (
            (command := ctx.bot.get_command("join")) is None
            or await command.can_run(ctx) is True
        ):
            await ctx.invoke(command)  # type: ignore

        assert ctx.voice_client is not None

        await checks.is_author_connected().predicate(ctx=ctx)  # type: ignore

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, source=slate.obsidian.Source.YOUTUBE)

        if not ctx.voice_client.is_playing():
            await ctx.voice_client.handle_track_end()
