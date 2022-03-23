# Future
from __future__ import annotations

# Standard Library
import datetime
import math
import urllib.parse
from typing import Literal, Optional

# Packages
import discord
from discord.ext import commands

# My stuff
from cd import checks, config, custom, exceptions, objects, paginators, utilities, values
from cd.bot import CD


async def setup(bot: CD) -> None:
    await bot.add_cog(Player(bot))


class Player(commands.Cog):
    """
    Player control commands.
    """

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: custom.Context) -> Literal[True]:  # pyright: reportIncompatibleMethodOverride=false

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Connecting

    @commands.command(name="connect", aliases=["join", "summon"])
    async def _connect(self, ctx: custom.Context) -> None:
        """
        Connects the bot to your voice channel.
        """

        assert isinstance(ctx.author, discord.Member)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise exceptions.EmbedError(description="You must be connected to a voice channel to use this command.")

        if ctx.voice_client and ctx.voice_client.voice_channel:
            raise exceptions.EmbedError(description=f"I'm already connected to {ctx.voice_client.voice_channel.mention}.")

        # slate's Player doesn't like this for some reason, investigate later.
        await ctx.author.voice.channel.connect(cls=custom.Player(text_channel=ctx.channel))  # type: ignore
        await ctx.send(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"**Connected** to {ctx.author.voice.channel}."
            )
        )

    @commands.command(name="disconnect", aliases=["dc", "leave", "destroy"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _disconnect(self, ctx: custom.Context) -> None:
        """
        Disconnects the bot from its voice channel.
        """

        assert ctx.voice_client is not None

        await ctx.send(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"**Disconnected** from {ctx.voice_client.voice_channel.mention}.")
        )
        await ctx.voice_client.disconnect()

    # Pausing

    @commands.command(name="pause", aliases=["stop"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _pause(self, ctx: custom.Context) -> None:
        """
        Pauses the player
        """

        assert ctx.voice_client is not None

        if ctx.voice_client.paused is True:
            raise exceptions.EmbedError(description="The player is already paused.")

        await ctx.voice_client.set_pause(True)
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="**Paused** the player."
            )
        )

    @commands.command(name="resume", aliases=["continue", "unpause"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _resume(self, ctx: custom.Context) -> None:
        """
        Resumes the player.
        """

        assert ctx.voice_client is not None

        if ctx.voice_client.paused is False:
            raise exceptions.EmbedError(description="The player is already playing.")

        await ctx.voice_client.set_pause(False)
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="**Resumed** the player."
            )
        )

    # Seeking

    @commands.command(name="seek", aliases=["scrub"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _seek(self, ctx: custom.Context, *, position: objects.ConvertedTime) -> None:
        """
        Seeks to a position in the current track.

        **Arguments:**
        `position`: The position to seek to. Can be in any of the following formats:
        - `ss`
        - `mm:ss`
        - `hh:mm:ss`
        - `30s`
        - `1m30s`
        - `1h30m`
        - `1h30m30s`
        - `1 hour 30 minutes 30 seconds`
        - `1 hour, 30 minutes, 30 seconds`
        - `1 hour and 30 minutes and 30 seconds`
        - etc, most permutations of these will work.
        """

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        milliseconds = position.seconds * 1000

        if 0 < milliseconds > ctx.voice_client.current.length:
            raise exceptions.EmbedError(
                description=f"**{position.original}** is not a valid position, the current track is only "
                            f"**{utilities.format_seconds(ctx.voice_client.current.length // 1000, friendly=True)}** long.",
            )

        await ctx.voice_client.set_position(milliseconds)
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"**Set** the players position to "
                            f"**{utilities.format_seconds(milliseconds // 1000, friendly=True)}**."
            )
        )

    @commands.command(name="fast-forward", aliases=["fast_forward", "fastforward", "ff", "forward", "fwd"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _fast_forward(self, ctx: custom.Context, *, time: objects.ConvertedTime) -> None:
        """
        Fast-forwards the current track by an amount of time.

        **Arguments:**
        `time`: The amount of time to fast-forward by. Can be in any of the following formats:
        - `ss`
        - `mm:ss`
        - `hh:mm:ss`
        - `30s`
        - `1m30s`
        - `1h30m`
        - `1h30m30s`
        - `1 hour 30 minutes 30 seconds`
        - `1 hour, 30 minutes, 30 seconds`
        - `1 hour and 30 minutes and 30 seconds`
        - etc, most permutations of these will work.
        """

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        milliseconds = time.seconds * 1000
        position = ctx.voice_client.position
        remaining = ctx.voice_client.current.length - position

        if milliseconds >= remaining:
            raise exceptions.EmbedError(
                description=f"**{time.original}** is too much time to fast forward, the current track only has "
                            f"**{utilities.format_seconds(remaining // 1000, friendly=True)}** remaining.",
            )

        await ctx.voice_client.set_position(position + milliseconds)
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"**Fast-forwarding** by **{utilities.format_seconds(time.seconds, friendly=True)}**, the "
                            f"players position is now **{utilities.format_seconds((position + milliseconds) // 1000, friendly=True)}**."
            )
        )

    @commands.command(name="rewind", aliases=["rwd", "backward", "bwd"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _rewind(self, ctx: custom.Context, *, time: objects.ConvertedTime) -> None:
        """
        Rewinds the current track by an amount of time.

        **Arguments:**
        `time`: The amount of time to rewind by. Can be in any of the following formats:
        - `ss`
        - `mm:ss`
        - `hh:mm:ss`
        - `30s`
        - `1m30s`
        - `1h30m`
        - `1h30m30s`
        - `1 hour 30 minutes 30 seconds`
        - `1 hour, 30 minutes, 30 seconds`
        - `1 hour and 30 minutes and 30 seconds`
        - etc, most permutations of these will work.
        """

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        milliseconds = time.seconds * 1000
        position = ctx.voice_client.position

        if milliseconds >= position:
            raise exceptions.EmbedError(
                description=f"**{time.original}** is too much time to rewind, only "
                            f"**{utilities.format_seconds(position // 1000, friendly=True)}** of the current track has passed."
            )

        await ctx.voice_client.set_position(position - milliseconds)
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"**Rewinding** by **{utilities.format_seconds(time.seconds, friendly=True)}**, the players "
                            f"position is now **{utilities.format_seconds((position - milliseconds) // 1000, friendly=True)}**."
            )
        )

    @commands.command(name="replay", aliases=["restart"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _replay(self, ctx: custom.Context) -> None:
        """
        Replays the current track.
        """

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        await ctx.voice_client.set_position(0)
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="**Replaying** the current track."
            )
        )

    # Now playing

    @commands.command(name="now-playing", aliases=["now_playing", "nowplaying", "np"])
    @checks.is_player_playing()
    @checks.is_player_connected()
    async def _now_playing(self, ctx: custom.Context) -> None:
        """
        Shows the current track.
        """

        assert ctx.voice_client is not None

        content, embed = await ctx.voice_client.controller.build_message()
        await ctx.send(content, embed=embed)  # type: ignore

    # Skipping

    @staticmethod
    async def _check_force_skip_permissions(ctx: custom.Context) -> None:

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
        guild_config = await ctx.bot.manager.get_guild_config(ctx.guild.id)

        if guild_config.dj_role_id:
            if role := ctx.guild.get_role(guild_config.dj_role_id):
                _checks.append(commands.has_role(role.id))
            else:
                await guild_config.set_dj_role_id(None)

        try:
            # noinspection PyUnresolvedReferences
            await commands.check_any(*_checks).predicate(ctx=ctx)
        except (commands.CheckAnyFailure, commands.MissingRole):
            raise exceptions.EmbedError(description="You don't have permission to force skip.")

    @commands.command(name="force-skip", aliases=["force_skip", "forceskip", "fs", "skipto"])
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _force_skip(self, ctx: custom.Context, amount: int = 0) -> None:
        """
        Force skips tracks in the queue.

        **Arguments:**
        `amount`: An optional amount of tracks to skip, defaults to 1.

        **Note:**
        You can only use this command if you meet one (or more) of the following requirements:
        - You are the owner of the bot.
        - You are the owner of this server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permissions.
        - You have the servers DJ role.
        """

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
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"Skipped **{amount or 1}** track{'s' if (amount or 1) != 1 else ''}."
            )
        )

        ctx.voice_client.skip_request_ids.clear()

    @commands.command(name="skip", aliases=["vote-skip", "vote_skip", "voteskip", "vs"])
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _skip(self, ctx: custom.Context) -> None:
        """
        Starts a vote-skip for the current track.

        **Note:**
        If you meet one or more of the following conditions, the track will be force skipped:
        - You are the owner of the bot.
        - You are the owner of this server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permissions.
        - You have the servers DJ role.
        - You are the requester of the current track.
        """

        try:
            await self._check_force_skip_permissions(ctx)
            await self._force_skip(ctx, amount=0)
            return
        except exceptions.EmbedError:
            pass

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None
        assert ctx.voice_client.current.requester is not None

        if ctx.author not in ctx.voice_client.listeners:
            raise exceptions.EmbedError(description="You can't vote to skip because you are currently deafened.")

        async def skip() -> None:

            assert ctx.voice_client is not None

            await ctx.voice_client.stop()
            await ctx.reply(
                embed=utilities.embed(
                    colour=values.GREEN,
                    description="Skipped the current track.")
            )
            ctx.voice_client.skip_request_ids.clear()

        if ctx.author.id == ctx.voice_client.current.requester.id:
            await skip()
            return

        if ctx.author.id in ctx.voice_client.skip_request_ids:

            ctx.voice_client.skip_request_ids.remove(ctx.author.id)
            await ctx.reply(
                embed=utilities.embed(
                    colour=values.GREEN,
                    description="**Removed** your vote to skip."
                )
            )
            return

        skips_needed = math.floor(75 * len(ctx.voice_client.listeners) / 100)

        if len(ctx.voice_client.listeners) < 3 or (len(ctx.voice_client.skip_request_ids) + 1) >= skips_needed:
            await skip()
            return

        ctx.voice_client.skip_request_ids.add(ctx.author.id)
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"**Added** your vote to skip, now at **{len(ctx.voice_client.skip_request_ids)}** out of **{skips_needed}** votes."
            )
        )

    # TODO: Refactor the following.

    @commands.command(name="lyrics")
    async def lyrics(self, ctx: custom.Context, *, query: Optional[str]) -> None:
        """
        Searches for lyrics.

        **Arguments:**
        `query`: The query to search for lyrics with.

        If `query` matches `spotify`, the lyric search will be performed with your current spotify track, if you are currently listening to one.
        If `query` matches `player`, the lyric search will be performed with the players current track, if there is one.
        """

        def get_spotify_query() -> str | None:

            assert isinstance(ctx.author, discord.Member)

            if not (activity := discord.utils.find(lambda x: isinstance(x, discord.Spotify), ctx.author.activities)):
                return None

            assert isinstance(activity, discord.Spotify)
            return f"{activity.artists[0]} - {activity.title}"

        def get_player_query() -> str | None:

            if not ctx.voice_client or ctx.voice_client.is_playing() is False:
                return None

            assert ctx.voice_client.current is not None
            return f"{ctx.voice_client.current.author} - {ctx.voice_client.current.title}"

        match query:
            case "spotify":
                if not (query := get_spotify_query()):
                    raise exceptions.EmbedError(description="You don't have an active spotify status.")
            case "player":
                if not (query := get_player_query()):
                    raise exceptions.EmbedError(description="I am not playing any tracks.")
            case _:
                if query is None and not (query := get_spotify_query()) and not (query := get_player_query()):
                    raise exceptions.EmbedError(description="You didn't specify a search query.")

        async with self.bot.session.get(
            url=f"https://api.openrobot.xyz/api/lyrics/{urllib.parse.quote_plus(query)}",
            headers={"Authorization": config.LYRIC_API_TOKEN}
        ) as response:

            match response.status:
                case 200:
                    data = await response.json()
                case 404:
                    raise exceptions.EmbedError(description=f"No lyrics were found for **{query}**.")
                case _:
                    raise exceptions.EmbedError(description=f"Lyrics are unavailable right now, please try again later.")

        entries = []

        for line in data["lyrics"].split("\n\n"):

            if len(entries) == 0 or len(entries[-1]) > 750 or len(entries[-1]) + len(line) > 750 or entries[-1].count("\n") > 20:
                entries.append(line)
            else:
                entries[-1] += f"\n\n{line}"

        paginator = paginators.EmbedPaginator(
            ctx=ctx,
            entries=entries,
            per_page=1,
            title=f"{data['title']} *by* {data['artist']}",
            thumbnail=data["images"]["track"],
        )
        await paginator.start()

    @staticmethod
    async def _do_status(ctx: custom.Context, *, format: Literal["png", "gif", "smooth_gif"]) -> None:

        assert isinstance(ctx.author, discord.Member)

        if not (activity := discord.utils.find(lambda x: isinstance(x, discord.Spotify), ctx.author.activities)):
            raise exceptions.EmbedError(description="You dont have an active spotify status.")

        assert isinstance(activity, discord.Spotify)

        url = await utilities.edit_image(
            url=activity.album_cover_url,
            bot=ctx.bot,
            function=utilities.spotify,
            # kwargs
            length=activity.duration.seconds,
            elapsed=(datetime.datetime.now(tz=datetime.timezone.utc) - activity.start).seconds,
            title=activity.title,
            artists=activity.artists,
            format=format,
        )
        await ctx.send(url)

    @commands.group(name="status", invoke_without_command=True)
    async def status(self, ctx: custom.Context) -> None:
        await self._do_status(ctx, format="png")

    @status.command(name="gif")
    async def status_gif(self, ctx: custom.Context) -> None:
        await self._do_status(ctx, format="gif")

    @status.command(name="smooth")
    @checks.is_owner()
    async def status_smooth(self, ctx: custom.Context) -> None:
        await self._do_status(ctx, format="smooth_gif")
