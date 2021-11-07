# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Packages
import discord
import slate
import slate.obsidian
import yarl

# My stuff
from core import values
from utilities import custom, enums, exceptions, utils


if TYPE_CHECKING:

    # My stuff
    from core.bot import CD

__all__ = (
    "Player",
)


class Player(slate.obsidian.Player["CD", custom.Context, "Player"]):

    def __init__(self, client: CD, channel: discord.VoiceChannel) -> None:
        super().__init__(client, channel)

        self._text_channel: discord.TextChannel | None = None
        self._controller: discord.Message | None = None

        self.queue: slate.Queue[slate.obsidian.Track] = slate.Queue()

        self._waiting: bool = False

    # Properties

    @property
    def text_channel(self) -> discord.TextChannel | None:
        return self._text_channel

    @property
    def voice_channel(self) -> discord.VoiceChannel:
        return self.channel

    # Events

    async def handle_track_start(self) -> None:
        self._controller = await self.send_controller(self.text_channel)

    async def handle_track_end(self, *, error: bool = False) -> None:

        await self.edit_controller(error=error)

        if self.is_playing() or self._waiting:
            return

        self._waiting = True
        track = await self.queue.get_wait()

        if track.source is slate.obsidian.Source.SPOTIFY:

            try:
                search = await self.search(f"{track.author} - {track.title}", source=slate.obsidian.Source.YOUTUBE, ctx=track.ctx)
            except exceptions.EmbedError as e:
                await self.send(embed=e.embed)
            else:
                track = search.tracks[0]

        await self.play(track)
        self._waiting = False

    async def handle_track_error(self) -> None:
        await self.handle_track_end(error=True)

    # Control

    async def send_controller(self, channel: discord.TextChannel | None, /) -> discord.Message | None:

        if not channel or not self.current:
            return

        embed = utils.embed(
            title="Now playing:",
            description=f"**[{self.current.title}]({self.current.uri})**\nBy **{self.current.author}**",
            thumbnail=self.current.thumbnail
        )

        embed.add_field(
            name="__Player info:__",
            value=f"**Paused:** {self.paused}\n"
                  f"**Loop mode:** {self.queue.loop_mode.name.title()}\n"
                  f"**Queue length:** {len(self.queue)}\n"
                  f"**Queue time:** {utils.format_seconds(sum(track.length for track in self.queue) // 1000, friendly=True)}\n",
        )
        embed.add_field(
            name="__Track info:__",
            value=f"**Time:** {utils.format_seconds(self.position // 1000)} / {utils.format_seconds(self.current.length // 1000)}\n"
                  f"**Is Stream:** {self.current.is_stream()}\n"
                  f"**Source:** {self.current.source.value.title()}\n"
                  f"**Requester:** {self.current.requester.mention if self.current.requester else 'N/A'}\n"
        )

        if not self.queue.is_empty():

            entries = [f"**{index + 1}.** [{entry.title}]({entry.uri})" for index, entry in enumerate(list(self.queue)[:3])]
            if len(self.queue) > 3:
                entries.append(f"**...**\n**{len(self.queue)}.** [{self.queue[-1].title}]({self.queue[-1].uri})")

            embed.add_field(
                name="__Up next:__",
                value="\n".join(entries),
                inline=False
            )

        return await channel.send(embed=embed)

    async def edit_controller(self, *, error: bool = False) -> None:

        if not self._controller:
            return

        if error:

            colour = values.RED

            try:
                old = self.queue._history[-1]
            except IndexError:
                description = "Something went wrong while playing a track."
            else:
                description = f"Something went wrong while playing **[{old.title}]({old.uri})** by **{old.author}**."

        else:

            colour = values.MAIN

            try:
                old = self.queue._history[-1]
            except IndexError:
                description = "Finished playing track."
            else:
                description = f"Finished playing **[{old.title}]({old.uri})** by **{old.author}**."

        await self._controller.edit(embed=utils.embed(colour=colour, description=description))
        self._controller = None

    # Misc

    async def send(self, *args, **kwargs) -> None:

        if not self.text_channel:
            return

        await self.text_channel.send(*args, **kwargs)

    async def search(
        self,
        query: str,
        /,
        *,
        source: slate.obsidian.Source,
        ctx: custom.Context | None,
    ) -> slate.obsidian.Result[custom.Context]:

        if (url := yarl.URL(query)) and url.host and url.scheme:
            source = slate.obsidian.Source.NONE

        try:
            search = await self._node.search(query, source=source, ctx=ctx)

        except slate.obsidian.NoResultsFound as error:
            raise exceptions.EmbedError(
                description=f"No {error.search_source.value.lower().replace('_', ' ')} {error.search_type.value}s were found for your search.",
            )

        except (slate.obsidian.SearchFailed, slate.HTTPError):
            raise exceptions.EmbedError(
                description="There was an error while searching for results.",
            )

        return search

    async def queue_search(
        self,
        query: str,
        /,
        *,
        source: slate.obsidian.Source,
        ctx: custom.Context,
        now: bool = False,
        next: bool = False,
        choose: bool = False,
    ) -> None:

        result = await self.search(query, source=source, ctx=ctx)

        if result.search_type in {slate.obsidian.SearchType.TRACK, slate.obsidian.SearchType.SEARCH_RESULT} or isinstance(result.result, list):
            tracks = [result.tracks[0]]
            description = f"Added the {result.search_source.value.lower()} track " \
                          f"[{result.tracks[0].title}]({result.tracks[0].uri}) to the queue."

        else:
            tracks = result.tracks
            description = f"Added the {result.search_source.value.lower()} {result.search_type.name.lower()} " \
                          f"[{result.result.name}]({result.result.url}) to the queue."

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=description
            )
        )

        self.queue.extend(tracks, position=0 if (now or next) else None)
        if now:
            await self.stop()
