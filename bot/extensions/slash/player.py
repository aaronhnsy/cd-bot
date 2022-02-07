# Future
from __future__ import annotations

# Standard Library
import math

# Packages
import discord
from discord.ext import commands

# My stuff
from core import values
from core.bot import CD
from utilities import checks, converters, custom, exceptions, slash, utils


def setup(bot: CD) -> None:
    bot.add_cog(SlashPlayer(bot))


class SlashPlayer(slash.ApplicationCog):

    # Connecting

    @slash.slash_command(name="join")
    async def join(self, ctx: slash.ApplicationContext) -> None:

        assert isinstance(ctx.author, discord.Member)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise exceptions.EmbedError(description="you must be connected to a voice channel to use this command.")

        if ctx.voice_client and ctx.voice_client.voice_channel:
            raise exceptions.EmbedError(description=f"i am already connected to {ctx.voice_client.voice_channel.mention}.")

        await ctx.author.voice.channel.connect(cls=custom.Player(text_channel=ctx.channel))  # type: ignore
        ctx.voice_client.text_channel = ctx.channel  # type: ignore

        assert ctx.voice_client is not None
        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"joined {ctx.voice_client.voice_channel.mention}."
            )
        )

    @slash.slash_command(name="disconnect")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def disconnect(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"left {ctx.voice_client.voice_channel.mention}.")
        )
        await ctx.voice_client.disconnect()

    # Pausing

    @slash.slash_command(name="pause")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def pause(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if ctx.voice_client.paused is True:
            raise exceptions.EmbedError(description="the current track is already paused.")

        await ctx.voice_client.set_pause(True)
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**paused** the current track."
            )
        )

    @slash.slash_command(name="resume")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def resume(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if ctx.voice_client.paused is False:
            raise exceptions.EmbedError(description="the current track is already playing.")

        await ctx.voice_client.set_pause(False)
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**resumed** the current track."
            )
        )

    # Seeking

    @slash.slash_command(name="seek")
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def seek(self, ctx: slash.ApplicationContext, time: str) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        converter = await converters.TimeConverter().convert(ctx, str(time))  # type: ignore
        milliseconds = converter.seconds * 1000

        if 0 < milliseconds > ctx.voice_client.current.length:
            raise exceptions.EmbedError(
                description=f"**{time}** is not a valid position. The track is only "
                            f"**{utils.format_seconds(ctx.voice_client.current.length // 1000, friendly=True)}** long.",
            )

        await ctx.voice_client.set_position(milliseconds)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"set the players position to **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
            )
        )

    @slash.slash_command(name="fast-forward")
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def fast_forward(self, ctx: slash.ApplicationContext, time: str) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        converter = await converters.TimeConverter().convert(ctx, str(time))  # type: ignore
        milliseconds = converter.seconds * 1000
        position = ctx.voice_client.position
        remaining = ctx.voice_client.current.length - position

        if milliseconds >= remaining:
            raise exceptions.EmbedError(
                description=f"**{time}** is too much time to seek forward, the current track only has "
                            f"**{utils.format_seconds(remaining // 1000, friendly=True)}** remaining.",
            )

        await ctx.voice_client.set_position(position + milliseconds)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"seeking forward **{utils.format_seconds(converter.seconds, friendly=True)}**, the players position is now "
                            f"**{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
            )
        )

    @slash.slash_command(name="rewind")
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def rewind(self, ctx: slash.ApplicationContext, time: str) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        converter = await converters.TimeConverter().convert(ctx, str(time))  # type: ignore
        milliseconds = converter.seconds * 1000
        position = ctx.voice_client.position

        if milliseconds >= position:
            raise exceptions.EmbedError(
                description=f"**{time}** is too much time to seek backward, only "
                            f"**{utils.format_seconds(position // 1000, friendly=True)}** of the current track has passed."
            )

        await ctx.voice_client.set_position(position - milliseconds)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"seeking backward **{utils.format_seconds(converter.seconds, friendly=True)}**, the players position is now "
                            f"**{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
            )
        )

    @slash.slash_command(name="replay")
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def replay(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        await ctx.voice_client.set_position(0)
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"replaying **[{ctx.voice_client.current.title}]({ctx.voice_client.current.uri})** by **{ctx.voice_client.current.author}**."
            )
        )

    # Now playing

    @slash.slash_command(name="now-playing")
    @checks.is_player_playing()
    @checks.is_player_connected()
    async def now_playing(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        await ctx.defer()
        await ctx.voice_client.send_controller(ctx.channel)  # type: ignore

    # Skipping

    @staticmethod
    async def _check_force_skip_permissions(ctx: slash.ApplicationContext) -> None:

        _checks = [
            checks.is_owner(),
            checks.is_guild_owner(),
            checks.has_any_permission(
                manage_channels=True,
                manage_roles=True,
                manage_guild=True,
                kick_members=True,
                ban_members=True,
                administrator=True,
            ),
        ]

        assert ctx.guild is not None
        guild_config = await ctx.bot.config.get_guild_config(ctx.guild.id)

        if guild_config.dj_role_id:
            if role := ctx.guild.get_role(guild_config.dj_role_id):
                _checks.append(commands.has_role(role.id))
            else:
                await guild_config.set_dj_role_id(None)

        try:
            await commands.check_any(*_checks).predicate(ctx=ctx)  # type: ignore
        except (commands.CheckAnyFailure, commands.MissingRole):
            raise exceptions.EmbedError(
                colour=values.RED,
                description="you don't have permission to force skip."
            )

    @slash.slash_command(name="force-skip")
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def force_skip(self, ctx: slash.ApplicationContext, amount: int = 0) -> None:

        await self._check_force_skip_permissions(ctx)

        assert ctx.voice_client is not None

        if amount:
            if 0 <= amount > len(ctx.voice_client.queue) + 1:
                raise exceptions.EmbedError(
                    description=f"**{amount}** is not a valid amount of tracks to skip, there are only"
                                f"**{len(ctx.voice_client.queue) + 1}** tracks in the queue."
                )
            del ctx.voice_client.queue[:amount - 1]

        await ctx.voice_client.stop()
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"skipped **{amount or 1}** track{'s' if (amount or 1) != 1 else ''}."
            )
        )

        ctx.voice_client.skip_request_ids.clear()

    @slash.slash_command(name="skip")
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def skip(self, ctx: slash.ApplicationContext) -> None:

        try:
            await self._check_force_skip_permissions(ctx)
            await self.force_skip.invoke(ctx, amount=0)
            return
        except exceptions.EmbedError:
            pass

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None
        assert ctx.voice_client.current.requester is not None

        if ctx.author not in ctx.voice_client.listeners:
            raise exceptions.EmbedError(description="you can't vote to skip as you are currently deafened.")

        async def skip() -> None:

            assert ctx.voice_client is not None

            await ctx.voice_client.stop()
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**skipped** the current track.")
            )
            ctx.voice_client.skip_request_ids.clear()

        if ctx.author.id == ctx.voice_client.current.requester.id:
            await skip()

        elif ctx.author.id in ctx.voice_client.skip_request_ids:

            ctx.voice_client.skip_request_ids.remove(ctx.author.id)
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**removed** your vote to skip."
                )
            )

        else:

            skips_needed = math.floor(75 * len(ctx.voice_client.listeners) / 100)

            if len(ctx.voice_client.listeners) < 3 or (len(ctx.voice_client.skip_request_ids) + 1) >= skips_needed:
                await skip()

            else:
                ctx.voice_client.skip_request_ids.add(ctx.author.id)
                await ctx.reply(
                    embed=utils.embed(
                        colour=values.GREEN,
                        description=f"**added** your vote to skip, now at **{len(ctx.voice_client.skip_request_ids)}** out of **{skips_needed}** votes."
                    )
                )
