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
from utilities import checks, converters, custom, exceptions, paginators, slash, utils


def setup(bot: CD) -> None:
    bot.add_cog(SlashPlayer(bot))


class SlashPlayer(slash.ApplicationCog):

    # Connecting

    @slash.slash_command(name="join", guild_id=240958773122957312)
    async def join(self, ctx: slash.ApplicationContext) -> None:

        assert isinstance(ctx.author, discord.Member)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise exceptions.EmbedError(description="You must be connected to a voice channel to use this command.")

        if ctx.voice_client and ctx.voice_client.voice_channel:
            raise exceptions.EmbedError(description=f"I am already connected to {ctx.voice_client.voice_channel.mention}.")

        await ctx.author.voice.channel.connect(cls=custom.Player)  # type: ignore
        ctx.voice_client.text_channel = ctx.channel  # type: ignore

        assert ctx.voice_client is not None
        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Joined {ctx.voice_client.voice_channel.mention}."
            )
        )

    @slash.slash_command(name="disconnect", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def disconnect(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        await ctx.send(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Left {ctx.voice_client.voice_channel.mention}.")
        )
        await ctx.voice_client.disconnect()

    # Pausing

    @slash.slash_command(name="pause", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def pause(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if ctx.voice_client.paused is True:
            raise exceptions.EmbedError(description="The played is already paused.")

        await ctx.voice_client.set_pause(True)
        await ctx.reply(embed=utils.embed(colour=values.GREEN, description="The player is now **paused**."))

    @slash.slash_command(name="resume", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def resume(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if ctx.voice_client.paused is False:
            raise exceptions.EmbedError(description="The player is not paused.")

        await ctx.voice_client.set_pause(False)
        await ctx.reply(embed=utils.embed(colour=values.GREEN, description="The player is now **resumed**."))

    # Seeking

    @slash.slash_command(name="seek", guild_id=240958773122957312)
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def seek(self, ctx: slash.ApplicationContext, time: str) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        time = await converters.TimeConverter().convert(ctx, str(time))  # type: ignore
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

    @slash.slash_command(name="fast-forward", guild_id=240958773122957312)
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def fast_forward(self, ctx: slash.ApplicationContext, time: str) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        time = await converters.TimeConverter().convert(ctx, str(time))  # type: ignore
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

    @slash.slash_command(name="rewind", guild_id=240958773122957312)
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def rewind(self, ctx: slash.ApplicationContext, time: str) -> None:

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None

        time = await converters.TimeConverter().convert(ctx, str(time))  # type: ignore
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

    @slash.slash_command(name="replay", guild_id=240958773122957312)
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
                description=f"Replaying **[{ctx.voice_client.current.title}]({ctx.voice_client.current.uri})** by **{ctx.voice_client.current.author}**."
            )
        )

    # Misc

    @slash.slash_command(name="now-playing", guild_id=240958773122957312)
    @checks.is_player_playing()
    @checks.is_player_connected()
    async def now_playing(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None
        await ctx.voice_client.send_controller(ctx.channel)  # type: ignore

        await ctx.defer()

    # Skipping

    @staticmethod
    async def _try_force_skip(ctx: slash.ApplicationContext) -> None:

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
                description="You do not have permission to force skip."
            )

    @slash.slash_command(name="force-skip", guild_id=240958773122957312)
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def force_skip(self, ctx: slash.ApplicationContext, amount: int = 0) -> None:

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

    @slash.slash_command(name="skip", guild_id=240958773122957312)
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def skip(self, ctx: slash.ApplicationContext) -> None:

        try:
            await self._try_force_skip(ctx)
            await self.force_skip.invoke(ctx, amount=None)
            return
        except exceptions.EmbedError:
            pass

        assert ctx.voice_client is not None
        assert ctx.voice_client.current is not None
        assert ctx.voice_client.current.requester is not None

        if ctx.author not in ctx.voice_client.listeners:
            raise exceptions.EmbedError(description="You can not vote skip as you are currently deafened.")

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

    @slash.slash_command(name="lyrics", guild_id=240958773122957312)
    async def lyrics(self, ctx: slash.ApplicationContext, *, query: str = "") -> None:

        def get_player_query() -> str:

            if not ctx.voice_client or ctx.voice_client.is_playing() is False:
                return ""

            assert ctx.voice_client.current is not None
            return f"{ctx.voice_client.current.author} - {ctx.voice_client.current.title}"

        match query:
            case "player":
                if not (query := get_player_query()):
                    raise exceptions.EmbedError(
                        colour=values.RED,
                        description="I am not playing any tracks.",
                    )
            case _:
                if not query and not (query := get_player_query()):
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
