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
    """
    Toggle and control different audio effects.
    """

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: commands.Context[CD]) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Effects

    @commands.command(name="8d")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _8d(self, ctx: custom.Context) -> None:
        """
        Toggles the 8D audio effect.

        This effect makes the audio sound like it's rotating around your head.
        """

        assert ctx.voice_client is not None

        if enums.Effect.ROTATION in ctx.voice_client.effects:
            ctx.voice_client.effects.remove(enums.Effect.ROTATION)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, rotation=slate.obsidian.Rotation()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**disabled** the **8d** audio effect."
                )
            )

        else:
            ctx.voice_client.effects.add(enums.Effect.ROTATION)
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
        """
        Toggles the nightcore audio effect.

        This effect slightly increases the speed and pitch of the audio.
        """

        assert ctx.voice_client is not None

        if enums.Effect.NIGHTCORE in ctx.voice_client.effects:
            ctx.voice_client.effects.remove(enums.Effect.NIGHTCORE)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, timescale=slate.obsidian.Timescale()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**disabled** the **nightcore** audio effect."
                )
            )

        else:
            ctx.voice_client.effects.add(enums.Effect.NIGHTCORE)
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
        """
        Toggles the mono audio effect.

        This effect makes the left and right audio channels play the same thing.

        **Note:** Enabling this effect will disable the left and right ear effects.
        """

        assert ctx.voice_client is not None

        if enums.Effect.MONO in ctx.voice_client.effects:
            ctx.voice_client.effects.remove(enums.Effect.MONO)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**disabled** the **mono** audio effect."
                )
            )

        else:

            ctx.voice_client.effects.add(enums.Effect.MONO)
            await ctx.voice_client.set_filter(
                slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix(left_to_right=1, right_to_left=1))
            )
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**enabled** the **mono** audio effect."
                )
            )

            if enums.Effect.LEFT_EAR in ctx.voice_client.effects:
                ctx.voice_client.effects.remove(enums.Effect.LEFT_EAR)
            if enums.Effect.RIGHT_EAR in ctx.voice_client.effects:
                ctx.voice_client.effects.remove(enums.Effect.RIGHT_EAR)

    @commands.command(name="left-ear", aliases=["left_ear", "leftear", "left", "le"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def left_ear(self, ctx: custom.Context) -> None:
        """
        Toggles the left ear audio effect.

        This effect makes the audio only come out of your left headphone/speaker/earbud.

        **Note:** Enabling this effect will disable the mono and right ear effects.
        """

        assert ctx.voice_client is not None

        if enums.Effect.LEFT_EAR in ctx.voice_client.effects:
            ctx.voice_client.effects.remove(enums.Effect.LEFT_EAR)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**disabled** the **left-ear** audio effect."
                )
            )

        else:

            ctx.voice_client.effects.add(enums.Effect.LEFT_EAR)
            await ctx.voice_client.set_filter(
                slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix(right_to_right=0, right_to_left=1))
            )
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**enabled** the **left-ear** audio effect."
                )
            )

            if enums.Effect.MONO in ctx.voice_client.effects:
                ctx.voice_client.effects.remove(enums.Effect.MONO)
            if enums.Effect.RIGHT_EAR in ctx.voice_client.effects:
                ctx.voice_client.effects.remove(enums.Effect.RIGHT_EAR)

    @commands.command(name="right-ear", aliases=["right_ear", "rightear", "right", "re"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def right_ear(self, ctx: custom.Context) -> None:
        """
        Toggles the right ear audio effect.

        This effect makes the audio only come out of your right headphone/speaker/earbud.

        **Note:** Enabling this effect will disable the mono and left ear effects.
        """

        assert ctx.voice_client is not None

        if enums.Effect.RIGHT_EAR in ctx.voice_client.effects:
            ctx.voice_client.effects.remove(enums.Effect.RIGHT_EAR)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**disabled** the **right-ear** audio effect."
                )
            )

        else:

            ctx.voice_client.effects.add(enums.Effect.RIGHT_EAR)
            await ctx.voice_client.set_filter(
                slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix(left_to_left=0, left_to_right=1))
            )
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**enabled** the **right-ear** audio effect."
                )
            )

            if enums.Effect.LEFT_EAR in ctx.voice_client.effects:
                ctx.voice_client.effects.remove(enums.Effect.LEFT_EAR)
            if enums.Effect.MONO in ctx.voice_client.effects:
                ctx.voice_client.effects.remove(enums.Effect.MONO)

    @commands.command(name="reset")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def reset(self, ctx: custom.Context) -> None:
        """
        Disables all audio effects.
        """

        assert ctx.voice_client is not None

        ctx.voice_client.effects.clear()
        await ctx.voice_client.set_filter(slate.obsidian.Filter())
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**disabled** all audio effects."
            )
        )
