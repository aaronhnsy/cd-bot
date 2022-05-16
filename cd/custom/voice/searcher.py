# Future
from __future__ import annotations

# Packages
import discord
import slate
import spotipy
import yarl

# Local
from cd import custom, exceptions, utilities, values


__all__ = (
    "Searcher",
)


class SearcherSelect(discord.ui.Select["SearcherView"]):

    def __init__(self) -> None:

        assert self.view is not None

        super().__init__(
            placeholder="Select some tracks:",
            max_values=len(self.view.search.tracks[:25]),
            options=[
                discord.SelectOption(
                    label=f"{track.title[:100]}",
                    value=f"{index}",
                    description=f"by {(track.author or 'Unknown')[:95]}"
                ) for index, track in enumerate(self.view.search.tracks[:25])
            ]
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        assert self.view.ctx.player is not None

        # Defer the interaction response because we
        # don't need to it to respond.
        await interaction.response.defer()

        # Get the users selected tracks and construct
        # an appropriate embed.
        tracks = [self.view.search.tracks[int(index)] for index in self.values]

        if len(tracks) == 1:
            description = f"Added the **{self.view.search.source.value.title()}** track " \
                          f"**[{discord.utils.escape_markdown(tracks[0].title)}]({tracks[0].uri})** " \
                          f"by **{discord.utils.escape_markdown(tracks[0].author or 'Unknown')}** to the queue."
        else:
            description = "Added your selected tracks to the queue."

        embed = utilities.embed(
            colour=values.GREEN,
            description=description
        )

        # Update the select menus state.
        self.disabled = True
        self.placeholder = "Done!"

        # Update the original message response with
        # the new embed and view.
        try:
            await self.view.message.edit(embed=embed, view=self.view)
        except (discord.NotFound, discord.HTTPException):
            pass

        # Add the selected tracks to the queue and
        # update the players' controller message.
        self.view.ctx.player.queue.extend(
            [custom.QueueItem(track) for track in tracks],
            position=0 if (self.view.play_next or self.view.play_now) else None
        )
        if self.view.play_now:
            await self.view.ctx.player.stop()
        if not self.view.ctx.player.is_playing():
            await self.view.ctx.player._play_next()

        await self.view.ctx.player.controller.update_current_message()


class SearcherView(discord.ui.View):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        search: slate.Search,
        play_next: bool = False,
        play_now: bool = False
    ) -> None:
        super().__init__(timeout=60)

        self.ctx: custom.Context = ctx
        self.search: slate.Search = search
        self.play_next: bool = play_next
        self.play_now: bool = play_now

        self.message: discord.Message = utilities.MISSING

        self.select: SearcherSelect = SearcherSelect()
        self.add_item(self.select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if interaction.user and interaction.user.id in (self.ctx.author.id, *values.OWNER_IDS):
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

        try:
            await self.message.edit(view=self)
        except (discord.NotFound, discord.HTTPException):
            pass


class Searcher:

    def __init__(
        self,
        *,
        player: custom.Player
    ) -> None:

        self.player: custom.Player = player

    async def search(
        self,
        query: str,
        /, *,
        source: slate.Source,
        ctx: custom.Context,
    ) -> slate.Search:

        if (url := yarl.URL(query)) and url.host and url.scheme:
            source = slate.Source.NONE

        try:
            search = await self.player.node.search(query, source=source, ctx=ctx)

        except slate.NoResultsFound as error:
            raise exceptions.EmbedError(
                description=f"No **{error.source.value.replace('_', ' ').title()}** {error.type}s were found for "
                            f"your search.",
            )

        except (slate.SearchFailed, slate.HTTPError):
            raise exceptions.EmbedError(
                description="There was an error while searching for results, please try again later.",
                view=discord.ui.View().add_item(
                    discord.ui.Button(label="Support Server", url=values.SUPPORT_LINK)
                )
            )

        return search

    async def queue(
        self,
        query: str,
        /, *,
        source: slate.Source,
        ctx: custom.Context,
        play_next: bool = False,
        play_now: bool = False,
        start_time: int = 0,
    ) -> None:

        search = await self.search(query, source=source, ctx=ctx)
        position = 0 if (play_next or play_now) else None

        if (
                isinstance(search.result, (spotipy.Album, spotipy.Playlist, spotipy.Artist, slate.Collection))
                and
                getattr(search.result, "name", "").startswith("Search result for:") is False
        ):
            self.player.queue.extend(
                [custom.QueueItem(track) for track in search.tracks],
                position=position
            )
            embed = utilities.embed(
                colour=values.GREEN,
                description=f"Added the **{search.source.value.title()}** {search.type.lower()} "
                            f"**[{search.result.name}]({search.result.url})** to the queue."
            )
        else:
            self.player.queue.put(
                custom.QueueItem(search.tracks[0], start_time=start_time),
                position=position
            )
            embed = utilities.embed(
                colour=values.GREEN,
                description=f"Added the **{search.source.value.title()}** track "
                            f"**[{discord.utils.escape_markdown(search.tracks[0].title)}]({search.tracks[0].uri})** "
                            f"by **{discord.utils.escape_markdown(search.tracks[0].author or 'Unknown')}** to the queue."
            )

        await ctx.reply(embed=embed)

        if play_now:
            await self.player.stop()
        if not self.player.is_playing():
            await self.player._play_next()

        await self.player.controller.update_current_message()

    async def select(
        self,
        query: str,
        /, *,
        source: slate.Source,
        ctx: custom.Context,
        play_next: bool = False,
        play_now: bool = False,
    ) -> None:

        search = await self.search(query, source=source, ctx=ctx)
        view = SearcherView(ctx=ctx, search=search, play_next=play_next, play_now=play_now)

        message = await ctx.reply(None, view=view)
        view.message = message
