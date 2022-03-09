# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import slate
from discord.ext import commands

# My stuff
from core import values
from core.bot import CD
from utilities import checks, custom, enums, utils


def setup(bot: CD) -> None:
    bot.add_cog(Effects(bot))


class Effects(commands.Cog):
    """
    Toggle different audio effects.
    """

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: commands.Context[CD]) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Controls

    EFFECT_MAP: dict[enums.Effect, dict[str, slate.BaseFilter]] = {
        enums.Effect.ROTATION:  {"rotation": slate.Rotation(rotation_hertz=0.5)},
        enums.Effect.NIGHTCORE: {"timescale": slate.Timescale(speed=1.12, pitch=1.12)},
        enums.Effect.MONO:      {"channel_mix": slate.ChannelMix(left_to_right=1, right_to_left=1)},
        enums.Effect.LEFT_EAR:  {"channel_mix": slate.ChannelMix(right_to_right=0, right_to_left=1)},
        enums.Effect.RIGHT_EAR: {"channel_mix": slate.ChannelMix(left_to_left=0, left_to_right=1)},
    }

    INVERSE_EFFECT_MAP: dict[enums.Effect, dict[str, slate.BaseFilter]] = {
        enums.Effect.ROTATION:  {"rotation": slate.Rotation()},
        enums.Effect.NIGHTCORE: {"timescale": slate.Timescale()},
        enums.Effect.MONO:      {"channel_mix": slate.ChannelMix()},
        enums.Effect.LEFT_EAR:  {"channel_mix": slate.ChannelMix()},
        enums.Effect.RIGHT_EAR: {"channel_mix": slate.ChannelMix()},
    }

    INCOMPATIBLE_EFFECTS: dict[enums.Effect, list[enums.Effect]] = {
        enums.Effect.MONO:      [enums.Effect.LEFT_EAR, enums.Effect.RIGHT_EAR],
        enums.Effect.LEFT_EAR:  [enums.Effect.MONO, enums.Effect.RIGHT_EAR],
        enums.Effect.RIGHT_EAR: [enums.Effect.MONO, enums.Effect.LEFT_EAR],
    }

    async def _toggle_effect(self, ctx: custom.Context, effect: enums.Effect) -> None:

        assert ctx.voice_client

        if effect in ctx.voice_client.effects:
            description = f"**Disabled** the **{effect.value}** audio effect."
            ctx.voice_client.effects.remove(effect)
            await ctx.voice_client.set_filter(slate.Filter(ctx.voice_client.filter, **self.INVERSE_EFFECT_MAP[effect]))

        else:
            description = f"**Enabled** the **{effect.value}** audio effect."
            ctx.voice_client.effects.add(effect)
            await ctx.voice_client.set_filter(slate.Filter(ctx.voice_client.filter, **self.EFFECT_MAP[effect]))

            if effect in self.INCOMPATIBLE_EFFECTS:
                for incompatible_effect in self.INCOMPATIBLE_EFFECTS[effect]:
                    try:
                        ctx.voice_client.effects.remove(incompatible_effect)
                    except KeyError:
                        pass

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=description
            )
        )

    @staticmethod
    async def _reset_effects(ctx: custom.Context) -> None:

        assert ctx.voice_client

        ctx.voice_client.effects.clear()
        await ctx.voice_client.set_filter(slate.Filter())
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**Disabled** all audio effects."
            )
        )

    # Commands

    @commands.command(name="8d")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _8d(self, ctx: custom.Context) -> None:
        """
        Toggles an 8D audio effect.

        This effect makes the audio sound like its rotating around your head.
        """

        await self._toggle_effect(ctx, enums.Effect.ROTATION)

    @commands.command(name="night-core", aliases=["night_core", "nightcore", "nc"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def night_core(self, ctx: custom.Context) -> None:
        """
        Toggles a nightcore audio effect.

        This effect slightly increases the speed and pitch of the audio.
        """

        await self._toggle_effect(ctx, enums.Effect.NIGHTCORE)

    @commands.command(name="mono")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def mono(self, ctx: custom.Context) -> None:
        """
        Toggles a mono audio effect.

        This effect makes the left and right audio channels play the same thing.

        **Note:** Enabling this effect will disable the `left-ear` and `right-ear` effects.
        """

        await self._toggle_effect(ctx, enums.Effect.MONO)

    @commands.command(name="left-ear", aliases=["left_ear", "leftear", "left"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def left_ear(self, ctx: custom.Context) -> None:
        """
        Toggles a left ear audio effect.

        This effect makes the audio only come out of your left headphone/speaker/earbud.

        **Note:** Enabling this effect will disable the `mono` and `right-ear` effects.
        """

        await self._toggle_effect(ctx, enums.Effect.LEFT_EAR)

    @commands.command(name="right-ear", aliases=["right_ear", "rightear", "right"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def right_ear(self, ctx: custom.Context) -> None:
        """
        Toggles a right ear audio effect.

        This effect makes the audio only come out of your right headphone/speaker/earbud.

        **Note:** Enabling this effect will disable the `mono` and `left-ear` effects.
        """

        await self._toggle_effect(ctx, enums.Effect.RIGHT_EAR)

    @commands.command(name="reset-effects", aliases=["reset_effects", "reseteffects"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def reset_effects(self, ctx: custom.Context) -> None:
        """
        Resets all audio effects.
        """

        assert ctx.voice_client is not None

        ctx.voice_client.effects.clear()
        await ctx.voice_client.set_filter(slate.Filter())
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**Disabled** all audio effects."
            )
        )
