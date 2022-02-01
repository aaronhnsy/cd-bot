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

    @slash.slash_command(name="8d", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _8d(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if enums.Filter.ROTATION in ctx.voice_client.filters:
            ctx.voice_client.filters.remove(enums.Filter.ROTATION)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, rotation=slate.obsidian.Rotation()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**Disabled** the **8d** audio effect."
                )
            )

        else:
            ctx.voice_client.filters.add(enums.Filter.ROTATION)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, rotation=slate.obsidian.Rotation(rotation_hertz=0.5)))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**Enabled** the **8d** audio effect."
                )
            )

    @slash.slash_command(name="night-core", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def night_core(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if enums.Filter.NIGHTCORE in ctx.voice_client.filters:
            ctx.voice_client.filters.remove(enums.Filter.NIGHTCORE)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, timescale=slate.obsidian.Timescale()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**Disabled** the **nightcore** audio effect."
                )
            )

        else:
            ctx.voice_client.filters.add(enums.Filter.NIGHTCORE)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, timescale=slate.obsidian.Timescale(speed=1.12, pitch=1.12)))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**Enabled** the **nightcore** audio effect."
                )
            )

    @slash.slash_command(name="mono", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def mono(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if enums.Filter.MONO in ctx.voice_client.filters:
            ctx.voice_client.filters.remove(enums.Filter.MONO)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**Disabled** the **mono** audio effect."
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
                    description="**Enabled** the **mono** audio effect."
                )
            )

            if enums.Filter.LEFT in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.LEFT)
            if enums.Filter.RIGHT in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.RIGHT)

    @slash.slash_command(name="left-ear", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def left_ear(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if enums.Filter.LEFT in ctx.voice_client.filters:
            ctx.voice_client.filters.remove(enums.Filter.LEFT)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**Disabled** the **left-ear** audio effect."
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
                    description="**Enabled** the **left-ear** audio effect."
                )
            )

            if enums.Filter.MONO in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.MONO)
            if enums.Filter.RIGHT in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.RIGHT)

    @slash.slash_command(name="right-ear", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def right_ear(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if enums.Filter.RIGHT in ctx.voice_client.filters:
            ctx.voice_client.filters.remove(enums.Filter.RIGHT)
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, channel_mix=slate.obsidian.ChannelMix()))
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**Disabled** the **right-ear** audio effect."
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
                    description="**Enabled** the **right-ear** audio effect."
                )
            )

            if enums.Filter.LEFT in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.LEFT)
            if enums.Filter.MONO in ctx.voice_client.filters:
                ctx.voice_client.filters.remove(enums.Filter.MONO)

    @slash.slash_command(name="reset", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def reset(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        ctx.voice_client.filters.clear()
        await ctx.voice_client.set_filter(slate.obsidian.Filter())
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**Disabled** all audio effects."
            )
        )
