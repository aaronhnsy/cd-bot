# Future
from __future__ import annotations

# Standard Library
import asyncio
from typing import TYPE_CHECKING

# Packages
import async_timeout
import discord
import slate

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


class Player(slate.Player["CD", custom.Context, "Player"]):

    def __init__(self, *, text_channel: discord.TextChannel) -> None:
        super().__init__()

        self.text_channel: discord.TextChannel = text_channel

        self.controller: custom.Controller = custom.Controller(voice_client=self)
        self.searcher: custom.Searcher = custom.Searcher(voice_client=self)
        self.queue: custom.Queue = custom.Queue()

        self.skip_request_ids: set[int] = set()
        self.effects: set[enums.Effect] = set()

        self.waiting: bool = False

    # Overrides

    async def stop(
        self,
        *,
        force: bool = False
    ) -> None:

        current = self._current
        await super().stop(force=force)
        self._current = current

    # Miscellaneous

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
                search = await self.searcher._search(track.isrc, source=slate.Source.YOUTUBE_MUSIC, ctx=track.ctx)
            except exceptions.EmbedError:
                try:
                    search = await self.searcher._search(track.isrc, source=slate.Source.YOUTUBE, ctx=track.ctx)
                except exceptions.EmbedError:
                    pass

        if search is None:
            try:
                search = await self.searcher._search(f"{track.author} - {track.title}", source=slate.Source.YOUTUBE, ctx=track.ctx)
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
