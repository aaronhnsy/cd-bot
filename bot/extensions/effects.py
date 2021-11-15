# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import slate.obsidian
from discord.ext import commands

# My stuff
from core import values
from core.bot import CD
from utilities import checks, custom, enums, utils


def setup(bot: CD) -> None:
    bot.add_cog(Effects(bot))


class Effects(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: commands.Context) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Effects

    @commands.command(name="8d")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _8d(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        if enums.Filter.ROTATION in ctx.voice_client.filters:
            ctx.voice_client.filters.remove(enums.Filter.ROTATION)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, rotation=slate.obsidian.Rotation()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**disabled** the **8d** audio effect."
                )
            )

        else:
            ctx.voice_client.filters.add(enums.Filter.ROTATION)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, rotation=slate.obsidian.Rotation(rotation_hertz=0.5)))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**enabled** the **8d** audio effect."
                )
            )

    @commands.command(name="night-core", aliases=["night_core", "nightcore", "nc"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def night_core(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        if enums.Filter.NIGHTCORE in ctx.voice_client.filters:
            ctx.voice_client.filters.remove(enums.Filter.NIGHTCORE)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, timescale=slate.obsidian.Timescale()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**disabled** the **nightcore** audio effect."
                )
            )

        else:
            ctx.voice_client.filters.add(enums.Filter.NIGHTCORE)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, timescale=slate.obsidian.Timescale(speed=1.12, pitch=1.12)))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**enabled** the **nightcore** audio effect."
                )
            )

    @commands.command(name="mono")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def mono(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        if enums.Filter.MONO in ctx.voice_client.filters:
            ctx.voice_client.filters.remove(enums.Filter.MONO)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**disabled** the **mono** audio effect."
                )
            )

        else:

            ctx.voice_client.filters.add(enums.Filter.MONO)
            await ctx.voice_client.set_filter(
                slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix(left_to_right=1, right_to_left=1))
            )
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**enabled** the **mono** audio effect."
                )
            )

            if enums.Filter.LEFT in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.LEFT)
            if enums.Filter.RIGHT in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.RIGHT)

    @commands.command(name="left-ear", aliases=["left_ear", "leftear", "left", "le"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def left_ear(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        if enums.Filter.LEFT in ctx.voice_client.filters:
            ctx.voice_client.filters.remove(enums.Filter.LEFT)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**disabled** the **left-ear** audio effect."
                )
            )

        else:

            ctx.voice_client.filters.add(enums.Filter.LEFT)
            await ctx.voice_client.set_filter(
                slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix(right_to_right=0, right_to_left=1))
            )
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**enabled** the **left-ear** audio effect."
                )
            )

            if enums.Filter.MONO in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.MONO)
            if enums.Filter.RIGHT in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.RIGHT)

    @commands.command(name="right-ear", aliases=["right_ear", "rightear", "right", "re"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def right_ear(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        if enums.Filter.RIGHT in ctx.voice_client.filters:
            ctx.voice_client.filters.remove(enums.Filter.RIGHT)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**disabled** the **right-ear** audio effect."
                )
            )

        else:

            ctx.voice_client.filters.add(enums.Filter.RIGHT)
            await ctx.voice_client.set_filter(
                slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix(left_to_left=0, left_to_right=1))
            )
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**enabled** the **right-ear** audio effect."
                )
            )

            if enums.Filter.LEFT in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.LEFT)
            if enums.Filter.MONO in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.MONO)

    @commands.command(name="reset")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def reset(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        ctx.voice_client.filters.clear()
        await ctx.voice_client.set_filter(slate.obsidian.Filter())
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**disabled** all audio effects."
            )
        )
