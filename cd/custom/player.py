# Future
from __future__ import annotations

# Standard Library
import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

# Packages
import async_timeout
import discord
import slate
import yarl

# My stuff
from cd import custom, enums, exceptions, utilities, values


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    # My stuff
    from cd.bot import CD


__all__ = (
    "Player",
)


#####################
# TRACK SEARCH VIEW #
#####################

class TrackSearchView(discord.ui.View):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        search: slate.Search[custom.Context],
        play_next: bool = False,
        play_now: bool = False
    ) -> None:
        super().__init__(timeout=60)

        self._ctx: custom.Context = ctx
        self._search: slate.Search[custom.Context] = search
        self._play_next: bool = play_next
        self._play_now: bool = play_now
        self._message: discord.Message = utilities.MISSING

        self._tracks: list[slate.Track[custom.Context]] = search.tracks[:25]

        self._select = TrackSearchSelect(
            placeholder="choose some tracks:",
            max_values=len(self._tracks),
            options=[
                discord.SelectOption(
                    label=f"{track.title[:100]}",
                    value=f"{index}",
                    description=f"by {(track.author or 'Unknown')[:95]}"
                ) for index, track in enumerate(self._tracks)
            ]
        )
        self.add_item(self._select)

    # Overrides

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user is not None and interaction.user.id == self._ctx.author.id

    async def on_timeout(self) -> None:
        await self.finish()

    # Utilities

    async def finish(self) -> None:

        self.stop()

        try:
            await self._message.delete()
        except (discord.NotFound, discord.HTTPException):
            pass


class TrackSearchSelect(discord.ui.Select[TrackSearchView]):

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None

        # Close view
        await self.view.finish()

        # Put selected tracks in queue.
        if not self.view._ctx.voice_client:
            return

        tracks = [self.view._tracks[int(index)] for index in self.values]
        position = 0 if (self.view._play_next or self.view._play_now) else None

        if len(tracks) > 1:
            await interaction.response.send_message(
                embed=utilities.embed(
                    colour=values.GREEN,
                    description="Added the selected tracks to the queue."
                )
            )
        else:
            await interaction.response.send_message(
                embed=utilities.embed(
                    colour=values.GREEN,
                    description=f"Added the **{self.view._search.source.value.title()}** track "
                                f"**[{discord.utils.escape_markdown(tracks[0].title)}]({tracks[0].uri})** "
                                f"by **{discord.utils.escape_markdown(tracks[0].author or 'unknown')}** to the queue."
                )
            )

        self.view._ctx.voice_client.queue.extend(tracks, position=position)

        if self.view._play_now:
            await self.view._ctx.voice_client.stop()
        if not self.view._ctx.voice_client.is_playing():
            await self.view._ctx.voice_client.handle_track_end(enums.TrackEndReason.NORMAL)


##############
# CONTROLLER #
##############

class ControllerView(discord.ui.View):

    def __init__(
        self,
        *,
        voice_client: Player
    ) -> None:
        super().__init__(timeout=None)

        self._voice_client: Player = voice_client

    # Buttons

    @discord.ui.button(label="Pause", emoji=values.PAUSE)
    async def _pause_or_resume(self, interaction: discord.Interaction, _: discord.ui.Button[ControllerView]) -> None:

        await interaction.response.defer()

        if self._voice_client.is_paused():
            await self._voice_client.set_pause(False)
            self._pause_or_resume.label = "Pause"
            self._pause_or_resume.emoji = values.PAUSE
        else:
            await self._voice_client.set_pause(True)
            self._pause_or_resume.label = "Resume"
            self._pause_or_resume.emoji = values.PLAY

        await self._voice_client.controller._update_view()

    @discord.ui.button(label="Next", emoji=values.NEXT)
    async def _next(self, interaction: discord.Interaction, _: discord.ui.Button[ControllerView]) -> None:

        await interaction.response.defer()
        await self._voice_client.stop()


class Controller:

    def __init__(
        self,
        *,
        voice_client: Player
    ) -> None:

        self._voice_client: Player = voice_client

        self._MESSAGE_BUILDERS: dict[enums.EmbedSize, Callable[..., Awaitable[tuple[str | None, discord.Embed | None]]]] = {
            enums.EmbedSize.IMAGE:  self._build_image,
            enums.EmbedSize.SMALL:  self._build_small,
            enums.EmbedSize.MEDIUM: self._build_medium,
            enums.EmbedSize.LARGE:  self._build_large,
        }

        self._message: discord.Message | None = None
        self._view: ControllerView = ControllerView(voice_client=self._voice_client)

    # Message building

    async def _build_image(self) -> tuple[str, None]:

        current = self._voice_client.current

        assert current is not None
        assert current.artwork_url is not None
        assert current.ctx is not None

        return (
            await utilities.edit_image(
                url=current.artwork_url,
                bot=current.ctx.bot,
                function=utilities.spotify,
                # kwargs
                length=current.length // 1000,
                elapsed=self._voice_client.position // 1000,
                title=current.title,
                artists=[current.author],
                format="png",
            ),
            None
        )

    async def _build_small(self) -> tuple[None, discord.Embed]:

        current = self._voice_client.current
        assert current is not None

        return (
            None,
            utilities.embed(
                colour=values.MAIN,
                title="Now Playing:",
                description=f"**[{discord.utils.escape_markdown(current.title)}]({current.uri})**\n"
                            f"by **{discord.utils.escape_markdown(current.author or 'Unknown')}**",
                thumbnail=current.artwork_url or "https://dummyimage.com/1280x720/000/ffffff.png&text=no+thumbnail+:(",
            )
        )

    async def _build_medium(self) -> tuple[None, discord.Embed]:

        current = self._voice_client.current
        assert current is not None

        _, embed = await self._build_small()

        assert isinstance(embed.description, str)
        embed.description += "\n\n" \
                             f"● **Requested by:** {getattr(current.requester, 'mention', None)}\n" \
                             f"● **Source:** {current.source.value.title()}\n" \
                             f"● **Paused:** {utilities.readable_bool(self._voice_client.paused).title()}\n" \
                             f"● **Effects:** {', '.join([effect.value for effect in self._voice_client.effects] or ['N/A'])}\n" \
                             f"● **Position:** {utilities.format_seconds(self._voice_client.position // 1000)} / {utilities.format_seconds(current.length // 1000)}\n"

        return _, embed

    async def _build_large(self) -> tuple[None, discord.Embed]:

        _, embed = await self._build_medium()

        if self._voice_client.queue._queue:
            entries = [
                f"**{index}. [{discord.utils.escape_markdown(entry.title)}]({entry.uri})**\n"
                f"**⤷** by **{discord.utils.escape_markdown(entry.author)}** | {utilities.format_seconds(entry.length // 1000, friendly=True)}\n"
                for index, entry in enumerate(self._voice_client.queue._queue[:3], start=1)
            ]

            assert isinstance(embed.description, str)
            embed.description += f"\n● **Up next ({len(self._voice_client.queue)}):**\n{''.join(entries)}"

        return _, embed

    async def build_message(self) -> dict[str, str | discord.Embed | None]:

        guild_config = await self._voice_client.bot.manager.get_guild_config(
            self._voice_client.voice_channel.guild.id
        )
        built = await self._MESSAGE_BUILDERS[guild_config.embed_size]()

        return {"content": built[0], "embed": built[1]}

    # Message handling

    async def _send_new_message(self) -> None:

        if not self._voice_client.current:
            return

        kwargs = await self.build_message()
        self._message = await self._voice_client.text_channel.send(**kwargs, view=self._view)

    async def _delete_old_message(self) -> None:

        if not self._message:
            return

        await self._message.delete()
        self._message = None

    async def _edit_old_message(self, reason: enums.TrackEndReason) -> None:

        if not self._message:
            return

        try:
            old = self._voice_client.queue._history[-1]
        except IndexError:
            track_info = "*Track info not found*"
            track_thumbnail = "https://dummyimage.com/1280x720/000/ffffff.png&text=thumbnail+not+found"
        else:
            track_info = f"**[{discord.utils.escape_markdown(old.title)}]({old.uri})**\n" \
                         f"by **{discord.utils.escape_markdown(old.author or 'Unknown')}**"
            track_thumbnail = old.artwork_url or "https://dummyimage.com/1280x720/000/ffffff.png&text=thumbnail+not+found"

        if reason != enums.TrackEndReason.NORMAL:
            colour = values.RED
            title = "Something went wrong!"
            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(label="Support Server", url=values.SUPPORT_LINK))
        else:
            colour = values.MAIN
            title = "Track ended:"
            view = None

        await self._message.edit(
            content=None,
            embed=utilities.embed(
                colour=colour,
                title=title,
                description=track_info,
                thumbnail=track_thumbnail,
            ),
            view=view
        )
        self._message = None

    async def _update_view(self) -> None:

        if not self._message:
            return

        await self._message.edit(view=self._view)

    # Events

    async def handle_track_start(self) -> None:
        await self._send_new_message()

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        guild_config = await self._voice_client.bot.manager.get_guild_config(self._voice_client.voice_channel.guild.id)

        if guild_config.delete_old_now_playing_messages:
            await self._delete_old_message()
        else:
            await self._edit_old_message(reason)


##########
# Player #
##########

class Player(slate.Player["CD", custom.Context, "Player"]):

    def __init__(self, text_channel: discord.TextChannel) -> None:
        super().__init__()

        self.text_channel: discord.TextChannel = text_channel

        self.controller: Controller = Controller(voice_client=self)
        self.queue: slate.Queue[slate.Track[custom.Context]] = slate.Queue()

        self.skip_request_ids: set[int] = set()
        self.effects: set[enums.Effect] = set()

        self.waiting: bool = False

    # Misc

    async def _disconnect_on_timeout(self) -> None:
        await self.text_channel.send(
            embed=utilities.embed(
                colour=values.MAIN,
                description=f"Left {self.voice_channel.mention}, nothing was added to the queue for two minutes."
            )
        )
        await self.disconnect()

    async def _convert_spotify_track(self, track: slate.Track[custom.Context]) -> slate.Track[custom.Context] | None:

        assert track.ctx is not None

        search = None

        if track.isrc:
            try:
                search = await self.search(track.isrc, source=slate.Source.YOUTUBE_MUSIC, ctx=track.ctx)
            except exceptions.EmbedError:
                try:
                    search = await self.search(track.isrc, source=slate.Source.YOUTUBE, ctx=track.ctx)
                except exceptions.EmbedError:
                    pass

        if search is None:
            try:
                search = await self.search(f"{track.author} - {track.title}", source=slate.Source.YOUTUBE, ctx=track.ctx)
            except exceptions.EmbedError:
                pass

        return search.tracks[0] if search else None

    # Events

    async def handle_track_start(self) -> None:

        # Update controller message.
        await self.controller.handle_track_start()

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        # Update controller message.
        await self.controller.handle_track_end(reason)

        # Set current track to None, otherwise is_playing
        # will return True even if the track has actually
        # ended.
        self._current = None

        # Don't continue if we are already waiting for a
        # new track or the player is already playing.

        if self.is_playing() or self.waiting:
            return

        self.waiting = True

        # Fetch the next track from the queue, disconnect
        # if there are no tracks in the queue and no new
        # ones are added for 180 seconds.

        if not self.queue.is_empty():
            track = self.queue.get()
            assert track is not None

        else:
            try:
                with async_timeout.timeout(180):
                    track = await self.queue.get_wait()
            except asyncio.TimeoutError:
                await self._disconnect_on_timeout()
                return

        # Convert Spotify tracks to YouTube tracks.

        if track.source is slate.Source.SPOTIFY:

            if not (_track := await self._convert_spotify_track(track)):
                await self.text_channel.send(
                    embed=utilities.embed(
                        colour=values.RED,
                        description=f"No YouTube tracks were found for the Spotify track "
                                    f"**[{discord.utils.escape_markdown(track.title)}]({track.uri})** "
                                    f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}**."
                    )
                )
                self.waiting = False
                await self.handle_track_end(enums.TrackEndReason.NORMAL)
                return

            track = _track

        # Play track.

        await self.play(track)
        self.waiting = False

    # Searching

    async def search(
        self,
        query: str,
        /, *,
        source: slate.Source,
        ctx: custom.Context
    ) -> slate.Search[custom.Context]:

        if (url := yarl.URL(query)) and url.host and url.scheme:
            source = slate.Source.NONE

        try:
            search = await self._node.search(query, source=source, ctx=ctx)

        except slate.NoResultsFound as error:
            raise exceptions.EmbedError(
                description=f"No {error.source.value.lower().replace('_', ' ')} {error.type}s were found for your search.",
            )

        except (slate.SearchFailed, slate.HTTPError):

            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(label="Support Server", url=values.SUPPORT_LINK))

            raise exceptions.EmbedError(
                description="There was an error while searching for results, try again later.",
                view=view,
            )

        return search

    async def queue_search(
        self,
        query: str,
        /, *,
        source: slate.Source,
        ctx: custom.Context,
        search_select: bool = False,
        play_next: bool = False,
        play_now: bool = False,
    ) -> None:

        search = await self.search(query, source=source, ctx=ctx)

        if search_select:

            view = TrackSearchView(ctx=ctx, search=search, play_next=play_next, play_now=play_now)
            message = await ctx.reply(values.ZWSP, view=view)
            view._message = message

        else:

            position = 0 if (play_next or play_now) else None

            if isinstance(search.result, list) or (isinstance(search.result, slate.Collection) and search.result.name.startswith("Search result for:")):

                track = search.tracks[0]
                await ctx.reply(
                    embed=utilities.embed(
                        colour=values.GREEN,
                        description=f"Added the **{search.source.value.title()}** track **[{discord.utils.escape_markdown(track.title)}]({track.uri})** "
                                    f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}** to the queue."
                    )
                )
                self.queue.put(track, position=position)

            else:

                tracks = search.tracks
                await ctx.reply(
                    embed=utilities.embed(
                        colour=values.GREEN,
                        description=f"Added the **{search.source.value.title()}** {search.type.lower()} **[{search.result.name}]({search.result.url})** "
                                    f"to the queue."
                    )
                )
                self.queue.extend(tracks, position=position)

            if self.is_playing() is False:
                await self.handle_track_end(enums.TrackEndReason.NORMAL)
            if play_now:
                await self.stop()
