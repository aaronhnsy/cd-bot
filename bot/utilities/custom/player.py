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


class SearchDropdown(discord.ui.Select):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        result: slate.obsidian.Result[custom.Context],
        next: bool = False,
        now: bool = False
    ) -> None:

        self.ctx: custom.Context = ctx
        self.result: slate.obsidian.Result[custom.Context] = result
        self.next: bool = next
        self.now: bool = now

        super().__init__(
            placeholder="Choose some tracks...",
            max_values=min(len(result.tracks), 25),
            options=[
                discord.SelectOption(
                    label=f"{track.title[:100]}",
                    value=str(index),
                    description=f"by {track.author[:95]}",
                ) for index, track in enumerate(result.tracks[:25])
            ]
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        # Finish view.

        assert self.view is not None

        self.disabled = True
        self.placeholder = "Selection done"

        await self.view.message.edit(view=self.view)
        self.view.stop()

        # Put selected tracks in queue.

        if not self.ctx.voice_client:
            return

        tracks = [self.result.tracks[int(index)] for index in self.values]
        position = 0 if (self.next or self.now) else None

        if len(tracks) > 1:
            await interaction.response.send_message(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="Added selected tracks to the queue."
                )
            )
            self.ctx.voice_client.queue.extend(tracks, position=position)
        else:
            await interaction.response.send_message(
                embed=utils.embed(
                    colour=values.GREEN,
                    description=f"Added the {self.result.search_source.value.lower()} track "
                                f"**[{discord.utils.escape_markdown(tracks[0].title)}]({tracks[0].uri})** "
                                f"by **{discord.utils.escape_markdown(tracks[0].author)}** to the queue."
                )
            )
            self.ctx.voice_client.queue.put(tracks[0], position=position)

        if self.now:
            await self.ctx.voice_client.stop()
        if not self.ctx.voice_client.is_playing():
            await self.ctx.voice_client.handle_track_end()


class SearchView(discord.ui.View):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        result: slate.obsidian.Result[custom.Context],
        next: bool = False,
        now: bool = False
    ) -> None:

        super().__init__(timeout=60)

        self.ctx: custom.Context = ctx
        self.message: discord.Message | None = None

        self.add_item(SearchDropdown(ctx=ctx, result=result, next=next, now=now))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user is not None and interaction.user.id == self.ctx.author.id

    async def on_timeout(self) -> None:

        self.children[0].disabled = True  # type: ignore
        self.children[0].placeholder = "Timed out"  # type: ignore

        if self.message:
            await self.message.edit(view=self)

        self.stop()


class Player(slate.obsidian.Player["CD", custom.Context, "Player"]):

    def __init__(self, client: CD, channel: discord.VoiceChannel) -> None:
        super().__init__(client, channel)

        self._text_channel: discord.TextChannel | None = None
        self._controller: discord.Message | None = None

        self.queue: slate.Queue[slate.obsidian.Track] = slate.Queue()
        self.skip_request_ids: set[int] = set()
        self.filters: set[enums.Filter] = set()

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

        self._current = None

        if self.is_playing() or self._waiting:
            return

        self._waiting = True
        track = await self.queue.get_wait()

        if track.source is slate.obsidian.Source.SPOTIFY:

            assert track.ctx is not None

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
            title="Now Playing:",
            description=f"**[{discord.utils.escape_markdown(self.current.title)}]({self.current.uri})**\n"
                        f"by **{discord.utils.escape_markdown(self.current.author)}**\n\n"
                        f"● **Requested by:** {getattr(self.current.requester, 'mention', None)}\n"
                        f"● **Source:** {self.current.source.value.title()}\n"
                        f"● **Paused:** {utils.readable_bool(self.paused).title()}\n"
                        f"● **Filters:** {', '.join([filter.value for filter in self.filters] or [f'N/A'])}\n"
                        f"● **Position:** {utils.format_seconds(self.position // 1000)} / {utils.format_seconds(self.current.length // 1000)}\n",
            thumbnail=self.current.artwork_url or "https://dummyimage.com/1280x720/000/ffffff.png&text=no+thumbnail+:(",
            colour=values.MAIN,
        )

        if self.queue._queue:

            entries = [
                f"**{index + 1}. [{discord.utils.escape_markdown(entry.title)}]({entry.uri})**\n"
                f"**⤷** by **{discord.utils.escape_markdown(entry.author)}** | {utils.format_seconds(entry.length // 1000, friendly=True)}\n"
                for index, entry in enumerate(self.queue._queue[:3])
            ]

            embed.description += f"\n" \
                                 f"● **Up next ({len(self.queue)}):**\n" \
                                 f"{''.join(entries)}"

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
        /, *,
        source: slate.obsidian.Source,
        ctx: custom.Context
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
                description="There was an error while searching for results, try again.",
            )

        return search

    async def queue_search(
        self,
        query: str,
        /, *,
        source: slate.obsidian.Source,
        ctx: custom.Context,
        next: bool = False,
        now: bool = False,
    ) -> None:

        result = await self.search(query, source=source, ctx=ctx)
        position = 0 if (next or now) else None

        if result.search_type in {slate.obsidian.SearchType.SEARCH_RESULT, slate.obsidian.SearchType.TRACK} or isinstance(result.result, list):
            track = result.tracks[0]
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description=f"Added the {result.search_source.value.lower()} track **[{discord.utils.escape_markdown(track.title)}]({track.uri})** by "
                                f"**{discord.utils.escape_markdown(track.author)}** to the queue."
                )
            )
            self.queue.put(track, position=position)

        else:
            tracks = result.tracks
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description=f"Added the {result.search_source.value.lower()} {result.search_type.name.lower()} "
                                f"**[{result.result.name}]({result.result.url})** to the queue."
                )
            )
            self.queue.extend(tracks, position=position)

        if now:
            await self.stop()
        elif not self.is_playing():
            await self.handle_track_end()

    async def choose_search(
        self,
        query: str,
        /, *,
        source: slate.obsidian.Source,
        ctx: custom.Context,
        next: bool = False,
        now: bool = False,
    ) -> None:

        result = await self.search(query, source=source, ctx=ctx)

        view = SearchView(ctx=ctx, result=result, next=next, now=now)
        message = await ctx.reply(values.ZWSP, view=view)
        view.message = message
