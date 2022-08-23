from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Literal

import slate
from discord.ext import commands

from cd import custom, enums, utilities, values
from cd.modules import voice


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "Effects",
)


FilterType = slate.Rotation | slate.Timescale | slate.ChannelMix


class Effects(commands.Cog):
    """
    Toggle different audio effects.
    """

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: custom.Context) -> Literal[True]:  # pyright: reportIncompatibleMethodOverride=false

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Controls

    EFFECT_MAP: dict[enums.Effect, dict[str, FilterType]] = {
        enums.Effect.Rotation:  {"rotation": slate.Rotation(speed=0.5)},
        enums.Effect.Nightcore: {"timescale": slate.Timescale(speed=1.12, pitch=1.12)},
        enums.Effect.Mono:      {"channel_mix": slate.ChannelMix(left_to_right=1, right_to_left=1)},
        enums.Effect.LeftEar:   {"channel_mix": slate.ChannelMix(right_to_right=0, right_to_left=1)},
        enums.Effect.RightEar:  {"channel_mix": slate.ChannelMix(left_to_left=0, left_to_right=1)},
    }

    INVERSE_EFFECT_MAP: dict[enums.Effect, dict[str, FilterType]] = {
        enums.Effect.Rotation:  {"rotation": slate.Rotation()},
        enums.Effect.Nightcore: {"timescale": slate.Timescale()},
        enums.Effect.Mono:      {"channel_mix": slate.ChannelMix()},
        enums.Effect.LeftEar:   {"channel_mix": slate.ChannelMix()},
        enums.Effect.RightEar:  {"channel_mix": slate.ChannelMix()},
    }

    INCOMPATIBLE_EFFECTS: dict[enums.Effect, list[enums.Effect]] = {
        enums.Effect.Mono:     [enums.Effect.LeftEar, enums.Effect.RightEar],
        enums.Effect.LeftEar:  [enums.Effect.Mono, enums.Effect.RightEar],
        enums.Effect.RightEar: [enums.Effect.Mono, enums.Effect.LeftEar],
    }

    async def _toggle_effect(self, ctx: custom.Context, effect: enums.Effect) -> None:

        assert ctx.player

        if effect in ctx.player.effects:
            description = f"Disabled the **{effect.value}** audio effect."
            ctx.player.effects.remove(effect)
            await ctx.player.set_filter(slate.Filter(ctx.player.filter, **self.INVERSE_EFFECT_MAP[effect]))

        else:
            description = f"Enabled the **{effect.value}** audio effect."
            ctx.player.effects.add(effect)
            await ctx.player.set_filter(slate.Filter(ctx.player.filter, **self.EFFECT_MAP[effect]))

            if effect in self.INCOMPATIBLE_EFFECTS:
                for incompatible_effect in self.INCOMPATIBLE_EFFECTS[effect]:
                    with contextlib.suppress(KeyError):
                        ctx.player.effects.remove(incompatible_effect)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=description
            )
        )

    # Commands

    @commands.hybrid_command(name="8d")
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def _8d(self, ctx: custom.Context) -> None:
        """
        Toggles an 8D audio effect.

        This effect makes the audio sound like its rotating around your head.
        """

        await self._toggle_effect(ctx, enums.Effect.Rotation)

    @commands.hybrid_command(name="nightcore", aliases=["night-core", "night_core", "nc"])
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def night_core(self, ctx: custom.Context) -> None:
        """
        Toggles a nightcore audio effect.

        This effect slightly increases the speed and pitch of the audio.
        """

        await self._toggle_effect(ctx, enums.Effect.Nightcore)

    @commands.hybrid_command(name="mono")
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def mono(self, ctx: custom.Context) -> None:
        """
        Toggles a mono audio effect.

        This effect makes the left and right audio channels play the same thing.

        **Note:** Enabling this effect will disable the `left-ear` and `right-ear` effects.
        """

        await self._toggle_effect(ctx, enums.Effect.Mono)

    @commands.hybrid_command(name="left-ear", aliases=["left_ear", "leftear", "left"])
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def left_ear(self, ctx: custom.Context) -> None:
        """
        Toggles a left ear audio effect.

        This effect makes the audio only come out of your left headphone/speaker/earbud.

        **Note:** Enabling this effect will disable the `mono` and `right-ear` effects.
        """

        await self._toggle_effect(ctx, enums.Effect.LeftEar)

    @commands.hybrid_command(name="right-ear", aliases=["right_ear", "rightear", "right"])
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def right_ear(self, ctx: custom.Context) -> None:
        """
        Toggles a right ear audio effect.

        This effect makes the audio only come out of your right headphone/speaker/earbud.

        **Note:** Enabling this effect will disable the `mono` and `left-ear` effects.
        """

        await self._toggle_effect(ctx, enums.Effect.RightEar)

    @commands.hybrid_command(name="reset-effects", aliases=["reset_effects", "reseteffects"])
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def reset_effects(self, ctx: custom.Context) -> None:
        """
        Resets all audio effects.
        """

        assert ctx.player is not None

        ctx.player.effects.clear()
        await ctx.player.set_filter(slate.Filter())
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="**Disabled** all audio effects."
            )
        )
