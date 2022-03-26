# Future
from __future__ import annotations

# Standard Library
import asyncio
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


Track = slate.Track[custom.Context]
Search = slate.Search[custom.Context]


class TrackSearchSelect(discord.ui.Select["TrackSearchView"]):

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await self.view.finish()

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
            await self.view._ctx.voice_client._play_next()

        await self.view._ctx.voice_client.controller.update_view()


class TrackSearchView(discord.ui.View):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        search: Search,
        play_next: bool = False,
        play_now: bool = False
    ) -> None:
        super().__init__(timeout=60)

        self._ctx: custom.Context = ctx
        self._search: Search = search
        self._play_next: bool = play_next
        self._play_now: bool = play_now
        self._message: discord.Message = utilities.MISSING

        self._tracks: list[Track] = search.tracks[:25]

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


class Player(slate.Player["CD", custom.Context, "Player"]):

    def __init__(
        self,
        text_channel: discord.TextChannel
    ) -> None:
        super().__init__()

        self.text_channel: discord.TextChannel = text_channel

        self.controller: custom.Controller = custom.Controller(voice_client=self)
        self.queue: custom.Queue = custom.Queue()

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

    async def _convert_spotify_track(self, track: Track) -> Track | None:

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

    async def _play_next(self) -> None:

        if self.is_playing() or self.waiting:
            return
        self.waiting = True

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
                await self._play_next()
                return

            track = _track

        await self.play(track)
        self.waiting = False

    # Events

    async def handle_track_start(self) -> None:

        # Update controller message.
        await self.controller.handle_track_start()

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        if reason is not enums.TrackEndReason.REPLACED:

            # Add current track to the queue history.
            assert self._current is not None
            self.queue.history.insert(0, self._current)

        # Update controller message.
        await self.controller.handle_track_end(reason)

        # Set current track to None so that is_playing()
        # returns False.
        self._current = None

        # Play the next track.
        await self._play_next()

    # Searching

    async def search(
        self,
        query: str,
        /, *,
        source: slate.Source,
        ctx: custom.Context
    ) -> Search:

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
                await self._play_next()
            if play_now:
                await self.stop()

            await self.controller.update_view()
