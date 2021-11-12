# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import discord
from discord.ext import commands

# My stuff
from core import values
from core.bot import CD
from utilities import checks, custom, exceptions, objects, utils


def setup(bot: CD) -> None:
    bot.add_cog(Player(bot))


class Player(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: commands.Context) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Connecting

    @commands.command(name="join", aliases=["j", "connect", "summon"])
    async def join(self, ctx: custom.Context) -> None:

        assert isinstance(ctx.author, discord.Member)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise exceptions.EmbedError(description="You must be connected to a voice channel to use this command.")

        if ctx.voice_client and ctx.voice_client.voice_channel:
            raise exceptions.EmbedError(description=f"I am already connected to {ctx.voice_client.voice_channel.mention}.")

        await ctx.author.voice.channel.connect(cls=custom.Player)  # type: ignore
        ctx.voice_client._text_channel = ctx.channel  # type: ignore

        assert ctx.voice_client is not None
        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Joined {ctx.voice_client.voice_channel.mention}."
            )
        )

    @commands.command(name="disconnect", aliases=["dc", "leave", "destroy"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def disconnect(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Left {ctx.voice_client.voice_channel.mention}.")
        )
        await ctx.voice_client.disconnect()

    # Pausing

    @commands.command(name="pause", aliases=["stop"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def pause(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        if ctx.voice_client.paused is True:
            raise exceptions.EmbedError(description="The played is already paused.")

        await ctx.voice_client.set_pause(True)
        await ctx.reply(embed=utils.embed(colour=values.GREEN, description="The player is now **paused**."))

    @commands.command(name="resume", aliases=["unpause", "continue"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def resume(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        if ctx.voice_client.paused is False:
            raise exceptions.EmbedError(description="The player is not paused.")

        await ctx.voice_client.set_pause(False)
        await ctx.reply(embed=utils.embed(colour=values.GREEN, description="The player is now **resumed**."))

    # Seeking

    @commands.command(name="seek", aliases=["scrub"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def seek(self, ctx: custom.Context, *, time: objects.Time) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        milliseconds = time.seconds * 1000

        if 0 < milliseconds > ctx.voice_client.current.length:
            raise exceptions.EmbedError(
                description=f"That is not a valid amount of time, please choose a time between "
                            f"**0s** and **{utils.format_seconds(ctx.voice_client.current.length // 1000, friendly=True)}**.",
            )

        await ctx.voice_client.set_position(milliseconds)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"The players position is now **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
            )
        )

    @commands.command(name="fast-forward", aliases=["fast_forward", "fastforward", "ff", "forward", "fwd"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def fast_forward(self, ctx: custom.Context, *, time: objects.Time) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        milliseconds = time.seconds * 1000
        position = ctx.voice_client.position
        remaining = ctx.voice_client.current.length - position

        if milliseconds >= remaining:
            raise exceptions.EmbedError(
                description=f"That was too much time to seek forward, try seeking forward an amount less than "
                            f"**{utils.format_seconds(remaining // 1000, friendly=True)}**.",
            )

        await ctx.voice_client.set_position(position + milliseconds)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Seeking forward **{utils.format_seconds(time.seconds, friendly=True)}**, the players position is now "
                            f"**{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
            )
        )

    @commands.command(name="rewind", aliases=["rwd", "backward", "bwd"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def rewind(self, ctx: custom.Context, *, time: objects.Time) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        milliseconds = time.seconds * 1000
        position = ctx.voice_client.position

        if milliseconds >= position:
            raise exceptions.EmbedError(
                description=f"That was too much time to seek backward, try seeking backward an amount less than "
                            f"**{utils.format_seconds(position // 1000, friendly=True)}**."
            )

        await ctx.voice_client.set_position(position - milliseconds)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Seeking backward **{utils.format_seconds(time.seconds, friendly=True)}**, the players position is now "
                            f"**{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
            )
        )

    @commands.command(name="replay", aliases=["restart"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def replay(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        await ctx.voice_client.set_position(0)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Replaying **[{ctx.voice_client.current.title}]({ctx.voice_client.current.uri})** by **{ctx.voice_client.current.author}**."
            )
        )

    #
