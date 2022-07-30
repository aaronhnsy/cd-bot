from __future__ import annotations

import asyncio
import contextlib
from typing import TYPE_CHECKING

import async_timeout
import discord
import slate

from cd import custom, enums, exceptions, utilities, values
from cd.modules import voice


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from cd.bot import SkeletonClique


__all__ = (
    "Player",
)


class Player(slate.Player["SkeletonClique", "Player"]):

    def __init__(
        self,
        *,
        text_channel: discord.abc.MessageableChannel
    ) -> None:
        super().__init__()

        self.text_channel: discord.TextChannel = text_channel  # type: ignore

        self.controller: voice.Controller = voice.Controller(player=self)
        self.searcher: voice.Searcher = voice.Searcher(player=self)
        self.queue: voice.Queue = voice.Queue()

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

    async def _convert_spotify_track(self, track: slate.Track) -> slate.Track | None:

        ctx: custom.Context = track.extras["ctx"]
        start_time: int = track.extras["start_time"]
        search = None

        if track.isrc:
            try:
                search = await self.searcher.search(
                    f"\"{track.isrc}\"",
                    source=slate.Source.YOUTUBE_MUSIC,
                    ctx=ctx,
                    start_time=start_time
                )
            except exceptions.EmbedError:
                with contextlib.suppress(exceptions.EmbedError):
                    search = await self.searcher.search(
                        f"\"{track.isrc}\"",
                        source=slate.Source.YOUTUBE,
                        ctx=ctx,
                        start_time=start_time
                    )

        if search is None:
            with contextlib.suppress(exceptions.EmbedError):
                search = await self.searcher.search(
                    f"{track.author} - {track.title}",
                    source=slate.Source.YOUTUBE,
                    ctx=ctx,
                    start_time=start_time
                )

        return search.tracks[0] if search else None

    async def play_next(self) -> None:

        if self.is_playing() or self.waiting:
            return
        self.waiting = True

        if self.queue.is_empty() is False:
            track = self.queue.get_from_front(put_into_history=False)

        else:
            try:
                with async_timeout.timeout(180):
                    track = await self.queue.wait_for_item(put_into_history=False)
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
                await self.play_next()
                return

            track = _track

        await self.play(track, start_time=track.extras["start_time"])
        self.waiting = False

    # Events

    async def handle_track_start(self) -> None:

        self.bot.dispatch("dashboard_track_start", player=self)

        # Update controller message.
        await self.controller.handle_track_start()

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        self.bot.dispatch("dashboard_track_end", player=self)

        if reason is not enums.TrackEndReason.REPLACED:

            # Add current track to the queue history.
            assert self._current is not None
            self.queue.put_into_history(position=0, item=self._current)

        # Update controller message.
        await self.controller.handle_track_end(reason)

        # Set current track to None so that is_playing()
        # returns False.
        self._current = None

        # Play the next track.
        await self.play_next()

    # Overrides

    async def connect(
        self,
        *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_mute: bool = False,
        self_deaf: bool = True,
    ) -> None:

        await super().connect(
            timeout=timeout,
            reconnect=reconnect,
            self_mute=self_mute,
            self_deaf=self_deaf,
        )

        self.bot.dispatch("dashboard_player_connect", player=self)

    async def disconnect(
        self,
        *,
        force: bool = False
    ) -> None:

        await super().disconnect(
            force=force
        )

        self.bot.dispatch("dashboard_player_disconnect", player=self)
