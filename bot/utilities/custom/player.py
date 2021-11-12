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
from utilities import custom, exceptions, utils


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
            placeholder='Choose a track...',
            options=[
                discord.SelectOption(
                    label=track.title,
                    description=f"by {track.author}",
                    value=str(index)
                ) for index, track in enumerate(result.tracks[:25])
            ]
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        self.view.stop()

        if not self.ctx.voice_client:
            return

        track = self.result.tracks[int(self.values[0])]

        await interaction.response.send_message(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Added the {self.result.search_source.value.lower()} track "
                            f"**[{track.title}]({track.uri})** by **{track.author}** to the queue."
            )
        )
        self.ctx.voice_client.queue.put(track, position=0 if (self.next or self.now) else None)

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

        self.ctx: custom.Context = ctx

        super().__init__()
        self.add_item(SearchDropdown(ctx=ctx, result=result, next=next, now=now))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user is not None and interaction.user.id == self.ctx.author.id


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

        self._current = None

        if self.is_playing() or self._waiting:
            return

        self._waiting = True
        track = await self.queue.get_wait()

        if track.source is slate.obsidian.Source.SPOTIFY:

            assert track.ctx is not None

            try:
                search = await self.search(f"{track.author} - {track.title}", source=slate.obsidian.Source.YOUTUBE_MUSIC, ctx=track.ctx)
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
            thumbnail=self.current.thumbnail,
            colour=values.MAIN,
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

        if result.search_type is slate.obsidian.SearchType.SEARCH_RESULT or isinstance(result.result, list):
            track = result.tracks[0]
            await ctx.reply(
                embed=utils.embed(
                    colour=values.GREEN,
                    description=f"Added the {result.search_source.value.lower()} track **[{track.title}]({track.uri})** by **{track.author}** to the queue."
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
        message = await ctx.send("Choose a track!", view=view)
        await view.wait()
        await message.delete()
