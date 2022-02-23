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
from core import values
from utilities import custom, enums, exceptions, imaging, objects, slash, utils


if TYPE_CHECKING:

    # My stuff
    from core.bot import CD


__all__ = (
    "Player",
)


class SearchView(discord.ui.View):

    def __init__(
        self,
        *,
        ctx: custom.Context | slash.ApplicationContext,
        search: slate.Search[custom.Context],
        play_next: bool = False,
        play_now: bool = False
    ) -> None:
        super().__init__(timeout=60)

        self.ctx: custom.Context | slash.ApplicationContext = ctx
        self.search: slate.Search[custom.Context] = search
        self.play_next: bool = play_next
        self.play_now: bool = play_now

        self.tracks: list[slate.Track[custom.Context]] = search.tracks[:25]

        self.add_item(
            SearchSelect(
                placeholder="choose some tracks:",
                max_values=len(self.tracks),
                options=[
                    discord.SelectOption(
                        label=f"{track.title[:100]}",
                        value=f"{index}",
                        description=f"by {(track.author or 'Unknown')[:95]}"
                    ) for index, track in enumerate(self.tracks)
                ]
            )
        )

        self.message: discord.Message | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user is not None and interaction.user.id == self.ctx.author.id

    async def on_timeout(self) -> None:
        await self._finish_selection(placeholder="timed out.")

    async def _finish_selection(self, *, placeholder: str) -> None:

        select: SearchSelect = self.children[0]  # type: ignore
        select.disabled = True
        select.placeholder = placeholder

        if self.message:
            await self.message.edit(view=self)

        self.stop()


class SearchSelect(discord.ui.Select[SearchView]):

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await self.view._finish_selection(placeholder="tracks selection over.")

        # Put selected tracks in queue.

        if not self.view.ctx.voice_client:
            return

        tracks = [self.view.tracks[int(index)] for index in self.values]
        position = 0 if (self.view.play_next or self.view.play_now) else None

        if len(tracks) > 1:
            await interaction.response.send_message(
                embed=utils.embed(
                    colour=values.GREEN,
                    description="**added** the selected tracks to the queue."
                )
            )
            self.view.ctx.voice_client.queue.extend(tracks, position=position)

        else:
            await interaction.response.send_message(
                embed=utils.embed(
                    colour=values.GREEN,
                    description=f"added the **{self.view.search.source.value.lower()}** track "
                                f"**[{discord.utils.escape_markdown(tracks[0].title)}]({tracks[0].uri})** "
                                f"by **{discord.utils.escape_markdown(tracks[0].author or 'unknown')}** to the queue."
                )
            )
            self.view.ctx.voice_client.queue.put(tracks[0], position=position)

        if self.view.play_now:
            await self.view.ctx.voice_client.stop()
        if not self.view.ctx.voice_client.is_playing():
            await self.view.ctx.voice_client.handle_track_end(enums.TrackEndReason.NORMAL)


##############
# Controller #
##############

class ControllerView(discord.ui.View):

    def __init__(self, voice_client: Player) -> None:
        super().__init__(timeout=None)

        self.voice_client: Player = voice_client

    @discord.ui.button(label="Pause", emoji=values.PAUSE)
    async def _pause_or_resume(self, _: discord.ui.Button[ControllerView], interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if self.voice_client.is_paused():
            await self.voice_client.set_pause(False)
            self._pause_or_resume.label = "Pause"
            self._pause_or_resume.emoji = values.PAUSE
        else:
            await self.voice_client.set_pause(True)
            self._pause_or_resume.label = "Resume"
            self._pause_or_resume.emoji = values.PLAY

        await self.voice_client.controller._update_view()

    @discord.ui.button(label="Next", emoji=values.NEXT)
    async def _next(self, _: discord.ui.Button[ControllerView], interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        await self.voice_client.stop()


class Controller:

    def __init__(self, voice_client: Player) -> None:

        self.voice_client: Player = voice_client

        self.message: discord.Message | None = None
        self.view: ControllerView = ControllerView(self.voice_client)

    # Embed

    async def _build_image(self) -> tuple[str, None]:

        assert self.voice_client.current is not None

        current = self.voice_client.current
        assert current.artwork_url is not None
        assert current.ctx is not None

        image = objects.FakeImage(url=current.artwork_url)

        url = await imaging.edit_image(
            ctx=current.ctx,
            edit_function=imaging.spotify,
            image=image,
            length=current.length // 1000,
            elapsed=self.voice_client.position // 1000,
            title=current.title,
            artists=[current.author],
            format="png",
        )
        return url, None

    def _build_small(self) -> tuple[None, discord.Embed]:

        assert self.voice_client.current is not None
        current = self.voice_client.current

        embed = utils.embed(
            colour=values.MAIN,
            title="Now Playing:",
            description=f"**[{discord.utils.escape_markdown(current.title)}]({current.uri})**\n"
                        f"by **{discord.utils.escape_markdown(current.author or 'Unknown')}**",
            thumbnail=current.artwork_url or "https://dummyimage.com/1280x720/000/ffffff.png&text=no+thumbnail+:(",
        )

        return None, embed

    def _build_medium(self) -> tuple[None, discord.Embed]:

        assert self.voice_client.current is not None
        current = self.voice_client.current

        _, embed = self._build_small()
        embed.description += "\n\n" \
                             f"● **Requested by:** {getattr(current.requester, 'mention', None)}\n" \
                             f"● **Source:** {current.source.value.title()}\n" \
                             f"● **Paused:** {utils.readable_bool(self.voice_client.paused).title()}\n" \
                             f"● **Effects:** {', '.join([effect.value for effect in self.voice_client.effects] or ['N/A'])}\n" \
                             f"● **Position:** {utils.format_seconds(self.voice_client.position // 1000)} / {utils.format_seconds(current.length // 1000)}\n"

        return None, embed

    def _build_large(self) -> tuple[None, discord.Embed]:

        _, embed = self._build_medium()

        if self.voice_client.queue._queue:
            entries = [
                f"**{index}. [{discord.utils.escape_markdown(entry.title)}]({entry.uri})**\n"
                f"**⤷** by **{discord.utils.escape_markdown(entry.author)}** | {utils.format_seconds(entry.length // 1000, friendly=True)}\n"
                for index, entry in enumerate(self.voice_client.queue._queue[:3], start=1)
            ]
            embed.description += f"\n● **Up next ({len(self.voice_client.queue)}):**\n{''.join(entries)}"

        return None, embed

    async def build_message(self) -> tuple[str | None, discord.Embed | None]:

        guild_config = await self.voice_client.bot.config.get_guild_config(self.voice_client.voice_channel.guild.id)

        match guild_config.embed_size:
            case enums.EmbedSize.IMAGE:
                content, embed = await self._build_image()
            case enums.EmbedSize.SMALL:
                content, embed = self._build_small()
            case enums.EmbedSize.MEDIUM:
                content, embed = self._build_medium()
            case enums.EmbedSize.LARGE:
                content, embed = self._build_large()
            case _:
                raise ValueError(f"Unknown embed size: {guild_config.embed_size}")

        return content, embed

    # Message

    async def _send_new_message(self) -> None:

        if not self.voice_client.current:
            return

        content, embed = await self.build_message()
        self.message = await self.voice_client.text_channel.send(content, embed=embed, view=self.view)  # type: ignore

    async def _delete_old_message(self) -> None:

        if not self.message:
            return

        await self.message.delete()
        self.message = None

    async def _edit_old_message(self, reason: enums.TrackEndReason) -> None:

        if not self.message:
            return

        try:
            old = self.voice_client.queue._history[-1]
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

        await self.message.edit(
            content=None,
            embed=utils.embed(
                colour=colour,
                title=title,
                description=track_info,
                thumbnail=track_thumbnail,
            ),
            view=view
        )
        self.message = None

    async def _update_view(self) -> None:

        if not self.message:
            return

        await self.message.edit(view=self.view)

    # Events

    async def handle_track_start(self) -> None:
        await self._send_new_message()

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        guild_config = await self.voice_client.bot.config.get_guild_config(self.voice_client.voice_channel.guild.id)

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

        self.controller: Controller = Controller(self)
        self.queue: slate.Queue[slate.Track[custom.Context]] = slate.Queue()

        self.skip_request_ids: set[int] = set()
        self.effects: set[enums.Effect] = set()

        self.waiting: bool = False

    # Misc

    async def _disconnect_on_timeout(self) -> None:
        await self.text_channel.send(
            embed=utils.embed(
                colour=values.MAIN,
                description=f"Left {self.voice_channel.mention}, nothing was added to the queue for two minutes."
            )
        )
        await self.disconnect()

    async def _convert_spotify_track(self, track: slate.Track[custom.Context]) -> slate.Track[custom.Context]:

        assert track.ctx is not None
        title = track.isrc or f"{track.author} - {track.title}"

        try:
            search = await self.search(title, source=slate.Source.YOUTUBE_MUSIC, ctx=track.ctx)
        except exceptions.EmbedError:
            search = await self.search(title, source=slate.Source.YOUTUBE, ctx=track.ctx)

        return search.tracks[0]

    # Events

    async def handle_track_start(self) -> None:
        await self.controller.handle_track_start()

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        # Update controller message.
        await self.controller.handle_track_end(reason)

        # Set current to None, otherwise is_playing will be True even after the track has already ended.
        self._current = None

        #

        if self.is_playing() or self.waiting:
            return

        self.waiting = True

        # Fetch next track from queue.

        if self.queue.is_empty():
            try:
                with async_timeout.timeout(180):
                    track = await self.queue.get_wait()
            except asyncio.TimeoutError:
                await self._disconnect_on_timeout()
                return
        else:
            track = self.queue.get()
            assert track is not None

        # Convert spotify tracks to youtube tracks.

        if track.source is slate.Source.SPOTIFY:

            try:
                track = await self._convert_spotify_track(track)
            except exceptions.EmbedError:
                self.waiting = False
                await self.text_channel.send(
                    embed=utils.embed(
                        colour=values.RED,
                        description=f"no youtube tracks were found for **[{discord.utils.escape_markdown(track.title)}]({track.uri})** by **{discord.utils.escape_markdown(track.author or 'Unknown')}** on spotify."
                    )
                )
                await self.handle_track_end(enums.TrackEndReason.NORMAL)
                return

        # Play track.

        await self.play(track)
        self.waiting = False

    # Searching and playing

    async def search(
        self,
        query: str,
        /, *,
        source: slate.Source,
        ctx: custom.Context | slash.ApplicationContext
    ) -> slate.Search[custom.Context]:

        if (url := yarl.URL(query)) and url.host and url.scheme:
            source = slate.Source.NONE

        try:
            search = await self._node.search(query, source=source, ctx=ctx)  # type: ignore

        except slate.NoResultsFound as error:
            raise exceptions.EmbedError(
                colour=values.RED,
                description=f"no {error.source.value.lower().replace('_', ' ')} {error.type}s were found for your search.",
            )

        except (slate.SearchFailed, slate.HTTPError):

            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(label="Support Server", url=values.SUPPORT_LINK))

            raise exceptions.EmbedError(
                colour=values.RED,
                description="there was an error while searching for results, try again later.",
                view=view,
            )

        return search

    async def queue_search(
        self,
        query: str,
        /, *,
        source: slate.Source,
        ctx: custom.Context | slash.ApplicationContext,
        search_select: bool = False,
        play_next: bool = False,
        play_now: bool = False,
    ) -> None:

        search = await self.search(query, source=source, ctx=ctx)

        if search_select:

            view = SearchView(ctx=ctx, search=search, play_next=play_next, play_now=play_now)
            message = await ctx.reply(values.ZWSP, view=view)
            view.message = message

        else:

            position = 0 if (play_next or play_now) else None

            if isinstance(search.result, list) or (isinstance(search.result, slate.Collection) and search.result.name.startswith("Search result for:")):

                track = search.tracks[0]
                await ctx.reply(
                    embed=utils.embed(
                        colour=values.GREEN,
                        description=f"added the **{search.source.value.lower()}** track **[{discord.utils.escape_markdown(track.title)}]({track.uri})** "
                                    f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}** to the queue."
                    )
                )
                self.queue.put(track, position=position)

            else:

                tracks = search.tracks
                await ctx.reply(
                    embed=utils.embed(
                        colour=values.GREEN,
                        description=f"added the **{search.source.value.lower()}** {search.type.lower()} **[{search.result.name}]({search.result.url})** "
                                    f"to the queue."
                    )
                )
                self.queue.extend(tracks, position=position)

            if self.is_playing() is False:
                await self.handle_track_end(enums.TrackEndReason.NORMAL)
            if play_now:
                await self.stop()
