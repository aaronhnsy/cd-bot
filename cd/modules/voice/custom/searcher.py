from __future__ import annotations

import contextlib

import discord
import spotipy
import yarl
from discord.ext import lava

from cd import custom, exceptions, utilities, values
from cd.modules import voice


__all__ = (
    "Searcher",
)


class SearcherSelect(discord.ui.Select["SearcherView"]):

    def __init__(
        self,
        *,
        player: voice.Player,
        search: lava.Search,
        play_next: bool = False,
        play_now: bool = False,
    ) -> None:

        self.player: voice.Player = player
        self.search: lava.Search = search
        self.play_next: bool = play_next
        self.play_now: bool = play_now

        super().__init__(
            placeholder="Select some tracks:",
            max_values=len(search.tracks[:25]),
            options=[
                discord.SelectOption(
                    label=f"{discord.utils.escape_markdown(track.title)[:100]}",
                    value=f"{index}",
                    description=f"by {discord.utils.escape_markdown(track.author or 'Unknown')[:100]}"
                ) for index, track in enumerate(search.tracks[:25])
            ]

        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        tracks: list[lava.Track] | None = None
        track: lava.Track | None = None

        if len(self.values) > 1:
            tracks = [self.search.tracks[int(index)] for index in self.values]
            description = "Added your selected tracks to the queue."
        else:
            track = self.search.tracks[int(self.values[0])]
            description = f"Added the **{self.search.source.value.replace('_', ' ').title()}** track " \
                          f"**[{discord.utils.escape_markdown(track.title)}]({track.uri})** " \
                          f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}** to the queue."

        if self.play_next or self.play_now:
            self.player.queue.put_at_front(items=tracks, item=track)
        else:
            self.player.queue.put_at_end(items=tracks, item=track)

        self.disabled = True
        self.placeholder = "Done!"

        with contextlib.suppress(discord.NotFound, discord.HTTPException):
            await self.view.message.edit(
                embed=utilities.embed(
                    colour=values.GREEN,
                    description=description
                ),
                view=self.view
            )

        self.view.stop()

        if self.play_now:
            await self.player.stop()
        if not self.player.is_playing():
            await self.player.play_next()

        await self.player.controller.update_current_message()


class SearcherView(discord.ui.View):

    def __init__(
        self,
        *,
        player: voice.Player,
        search: lava.Search,
        play_next: bool = False,
        play_now: bool = False
    ) -> None:
        super().__init__(timeout=60)

        self.message: discord.Message = utilities.MISSING
        self.owner_id: int = utilities.MISSING

        self.select: SearcherSelect = SearcherSelect(
            player=player,
            search=search,
            play_next=play_next,
            play_now=play_now
        )
        self.add_item(self.select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if interaction.user and interaction.user.id in (self.owner_id, *values.OWNER_IDS):
            return True

        await interaction.response.send_message(
            embed=utilities.embed(
                colour=values.RED,
                description="This search menu does not belong to you."
            ),
            ephemeral=True
        )
        return False

    async def on_timeout(self) -> None:

        self.select.disabled = True
        self.select.placeholder = "Timed out!"

        with contextlib.suppress(discord.NotFound, discord.HTTPException):
            await self.message.edit(view=self)


class Searcher:

    def __init__(
        self,
        *,
        player: voice.Player
    ) -> None:
        self.player: voice.Player = player

    async def search(
        self,
        query: str,
        /, *,
        source: lava.Source,
        ctx: custom.Context,
        start_time: int | None = None
    ) -> lava.Search:

        if (url := yarl.URL(query)) and url.host and url.scheme:
            source = lava.Source.NONE

        try:
            search = await self.player.node.search(
                query,
                source=source,
                ctx=ctx,
                start_time=start_time
            )

        except lava.NoResultsFound as error:
            raise exceptions.EmbedError(
                description=f"No **{error.source.value.replace('_', ' ').title()}** {error.type.lower()}s were found "
                            f"for your search."
            ) from error

        except (lava.SearchFailed, lava.HTTPError) as e:
            raise exceptions.EmbedError(
                description="There was an error while searching for results, please try again later.",
                view=discord.ui.View().add_item(
                    discord.ui.Button(
                        label="Support Server",
                        url=values.SUPPORT_LINK
                    )
                )
            ) from e

        return search

    async def queue(
        self,
        query: str,
        /, *,
        source: lava.Source,
        ctx: custom.Context,
        play_next: bool = False,
        play_now: bool = False,
        start_time: int | None = None,
    ) -> None:

        search = await self.search(
            query,
            source=source,
            ctx=ctx,
            start_time=start_time
        )

        tracks: list[lava.Track] | None = None
        track: lava.Track | None = None

        if (
            isinstance(search.result, (spotipy.Album, spotipy.Playlist, spotipy.Artist, lava.Collection))
            and
            getattr(search.result, "name", "").startswith("Search result for:") is False
        ):
            tracks = search.tracks
            description = f"Added the **{search.source.value.replace('_', ' ').title()}** {search.type.lower()} " \
                          f"**[{search.result.name}]({search.result.url})** to the queue."

        else:
            track = search.tracks[0]
            description = f"Added the **{search.source.value.replace('_', ' ').title()}** track " \
                          f"**[{discord.utils.escape_markdown(track.title)}]({track.uri})** " \
                          f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}** to the queue."

        if play_next or play_now:
            self.player.queue.put_at_front(items=tracks, item=track)
        else:
            self.player.queue.put_at_end(items=tracks, item=track)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=description
            )
        )

        if play_now:
            await self.player.stop()
        if not self.player.is_playing():
            await self.player.play_next()

        await self.player.controller.update_current_message()

    async def select(
        self,
        query: str,
        /, *,
        source: lava.Source,
        ctx: custom.Context,
        play_next: bool = False,
        play_now: bool = False,
    ) -> None:

        search = await self.search(
            query,
            source=source,
            ctx=ctx
        )

        view = SearcherView(
            player=self.player,
            search=search,
            play_next=play_next,
            play_now=play_now
        )
        message = await ctx.reply(
            None,
            view=view
        )

        view.message = message
        view.owner_id = ctx.author.id
