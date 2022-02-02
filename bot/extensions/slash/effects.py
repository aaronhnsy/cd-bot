# Future
from __future__ import annotations

# Packages
import slate.obsidian

# My stuff
from core import values
from core.bot import CD
from utilities import checks, enums, slash, utils


def setup(bot: CD) -> None:
    bot.add_cog(SlashEffects(bot))


class SlashEffects(slash.ApplicationCog):

    EFFECT_MAP: dict[enums.Effect, dict[str, slate.obsidian.BaseFilter]] = {
        enums.Effect.ROTATION:  {"rotation": slate.obsidian.Rotation(rotation_hertz=0.5)},
        enums.Effect.NIGHTCORE: {"timescale": slate.obsidian.Timescale(speed=1.12, pitch=1.12)},
    }

    INVERSE_EFFECT_MAP: dict[enums.Effect, dict[str, slate.obsidian.BaseFilter]] = {
        enums.Effect.ROTATION:  {"rotation": slate.obsidian.Rotation()},
        enums.Effect.NIGHTCORE: {"timescale": slate.obsidian.Timescale()},
    }

    async def _toggle_effect(self, ctx: slash.ApplicationContext, effect: enums.Effect) -> None:

        assert ctx.voice_client

        if effect in ctx.voice_client.effects:
            description = f"**disabled** the **{effect.value}** audio effect."
            ctx.voice_client.effects.remove(effect)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, **self.INVERSE_EFFECT_MAP[effect]))
        else:
            description = f"**enabled** the **{effect.value}** audio effect."
            ctx.voice_client.effects.add(effect)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, **self.EFFECT_MAP[effect]))

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=description
            )
        )

    @staticmethod
    async def _reset_effects(ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client

        ctx.voice_client.effects.clear()
        await ctx.voice_client.set_filter(slate.obsidian.Filter())
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**disabled** all audio effects."
            )
        )

    # Commands

    @slash.slash_command(name="8d")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _8d(self, ctx: slash.ApplicationContext) -> None:
        await self._toggle_effect(ctx, enums.Effect.ROTATION)

    @slash.slash_command(name="nightcore")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def night_core(self, ctx: slash.ApplicationContext) -> None:
        await self._toggle_effect(ctx, enums.Effect.NIGHTCORE)

    @slash.slash_command(name="reset-effects")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def reset_effects(self, ctx: slash.ApplicationContext) -> None:
        await self._reset_effects(ctx)
