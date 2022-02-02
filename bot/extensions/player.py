# Future
from __future__ import annotations

# Standard Library
import math
from typing import Literal, Optional

# Packages
import discord
from discord.ext import commands

# My stuff
from core import values
from core.bot import CD
from utilities import checks, custom, exceptions, objects, paginators, utils


def setup(bot: CD) -> None:
    bot.add_cog(Player(bot))


class Player(commands.Cog):
    """
    Commands for controlling the player.
    """

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: commands.Context[CD]) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Connecting

    @commands.command(name="join", aliases=["j", "connect", "summon"])
    async def join(self, ctx: custom.Context) -> None:
        """
        Connects the bot to your voice channel.
        """

        assert isinstance(ctx.author, discord.Member)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise exceptions.EmbedError(description="you must be connected to a voice channel to use this command.")

        if ctx.voice_client and ctx.voice_client.voice_channel:
            raise exceptions.EmbedError(description=f"i am already connected to {ctx.voice_client.voice_channel.mention}.")

        await ctx.author.voice.channel.connect(cls=custom.Player)  # type: ignore
        ctx.voice_client.text_channel = ctx.channel  # type: ignore

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
        """
        Disconnects the bot from your voice channel.
        """

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
        """
        Pauses the current track.
        """

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

    @commands.command(name="resume", aliases=["unpause", "continue"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def resume(self, ctx: custom.Context) -> None:
        """
        Resumes the current track.
        """

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

    @commands.command(name="seek", aliases=["scrub"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def seek(self, ctx: custom.Context, *, time: objects.FakeTimeConverter) -> None:
        """
        Seeks to time in the current track.

        **Arguments:**
        `time`: The time to seek to, this can be in any of the following formats:
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
    async def fast_forward(self, ctx: custom.Context, *, time: objects.FakeTimeConverter) -> None:
        """
        Fast-forwards the current track by an amount of time.

        **Arguments:**
        `time`: The amount of time to fast-forward by, this can be in any of the following formats:
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
    async def rewind(self, ctx: custom.Context, *, time: objects.FakeTimeConverter) -> None:
        """
        Rewinds the current track by an amount of time.

        **Arguments:**
        `time`: The amount of time to rewind by, this can be in any of the following formats:
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
        """
        Replays the current track.
        """

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        await ctx.voice_client.set_position(0)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Replaying **[{ctx.voice_client.current.title}]({ctx.voice_client.current.uri})** by **{ctx.voice_client.current.author}**."
            )
        )

    # Misc

    @commands.command(name="now-playing", aliases=["now_playing", "nowplaying", "np"])
    @checks.is_player_playing()
    @checks.is_player_connected()
    async def now_playing(self, ctx: custom.Context) -> None:
        """
        Shows the current track.
        """

        assert ctx.voice_client is not None
        await ctx.voice_client.send_controller(ctx.channel)  # type: ignore

    # Skipping

    @staticmethod
    async def _try_force_skip(ctx: custom.Context) -> None:

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

    @commands.command(name="force-skip", aliases=["force_skip", "forceskip", "fs", "skipto"])
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def force_skip(self, ctx: custom.Context, amount: Optional[int]) -> None:
        """
        Force skips the current track.

        **Arguments:**
        `amount`: An optional amount of tracks to skip, defaults to 1.

        **Note:**
        You can only use this command if you meet one of the following requirements:
        - You are the owner of the bot.
        - You are the owner of the server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permission.
        - You have the servers DJ role.
        """

        await self._try_force_skip(ctx)

        assert ctx.voice_client is not None

        if amount:

            if 0 <= amount > len(ctx.voice_client.queue) + 1:
                raise exceptions.EmbedError(
                    description=f"There are not enough tracks in the queue to skip that many, try again with an amount between "
                                f"**1** and **{len(ctx.voice_client.queue) + 1}**.",
                )

            del ctx.voice_client.queue[:amount - 1]

        await ctx.voice_client.stop()
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Force skipped **{amount or 1}** track{'s' if (amount or 1) != 1 else ''}."
            )
        )
        ctx.voice_client.skip_request_ids.clear()

    @commands.command(name="vote-skip", aliases=["vote_skip", "voteskip", "vs", "skip", "s"])
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def vote_skip(self, ctx: custom.Context) -> None:
        """
        Starts a vote-skip for the current track.

        If you meet any of the following, the track will be force skipped:
        - You are the owner of the bot.
        - You are the owner of the server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permission.
        """

        try:
            await self._try_force_skip(ctx)
            await self.force_skip(ctx, amount=None)
            return
        except exceptions.EmbedError:
            pass

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None
        assert ctx.voice_client.current.requester is not None

        if ctx.author not in ctx.voice_client.listeners:
            raise exceptions.EmbedError(description="you can not vote skip as you are currently deafened.")

        async def skip() -> None:

            assert ctx.voice_client is not None

            await ctx.voice_client.stop()
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="Skipped the current track.")
            )
            ctx.voice_client.skip_request_ids.clear()

        if ctx.author.id == ctx.voice_client.current.requester.id:
            await skip()

        elif ctx.author.id in ctx.voice_client.skip_request_ids:

            ctx.voice_client.skip_request_ids.remove(ctx.author.id)
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="Removed your vote to skip."
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
                        description=f"Added your vote to skip, now at **{len(ctx.voice_client.skip_request_ids)}** out of **{skips_needed}** votes "
                                    f"needed to skip."
                    )
                )

    # Lyrics

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
                    raise exceptions.EmbedError(
                        colour=values.RED,
                        description="You don't have an active spotify status.",
                    )
            case "player":
                if not (query := get_player_query()):
                    raise exceptions.EmbedError(
                        colour=values.RED,
                        description="I am not playing any tracks.",
                    )
            case _:
                if query is None and not (query := get_spotify_query()) and not (query := get_player_query()):
                    raise exceptions.EmbedError(
                        colour=values.RED,
                        description="You didn't specify a search query.",
                    )

        async with self.bot.session.get(
                url="https://evan.lol/lyrics/search/top",
                params={"q": query},
        ) as response:

            match response.status:
                case 200:
                    data = await response.json()
                case 404:
                    raise exceptions.EmbedError(
                        colour=values.RED,
                        description=f"No lyrics were found for **{query}**.",
                    )
                case _:
                    raise exceptions.EmbedError(
                        colour=values.RED,
                        description=f"Lyrics are unavailable right now, please try again later."
                    )

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
            title=data["name"],
            url=f"https://open.spotify.com/track/{data['id']}",
            header=f"by: **{', '.join([artist['name'] for artist in data['artists']] or ['Unknown Artist'])}**\n\n",
            thumbnail=icon["url"] if (icon := data["album"].get("icon")) else None,
        )
        await paginator.start()
