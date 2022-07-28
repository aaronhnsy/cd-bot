# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Literal

# Packages
import discord
import slate
from discord.ext import commands

# Local
from cd import custom, exceptions, paginators, utilities, values
from cd.modules import voice


if TYPE_CHECKING:
    # Local
    from cd.bot import SkeletonClique


__all__ = (
    "Queue",
)


class Queue(commands.Cog):
    """
    Queue management commands.
    """

    def __init__(self, bot: SkeletonClique) -> None:
        self.bot: SkeletonClique = bot

    def cog_check(self, ctx: custom.Context) -> Literal[True]:  # pyright: reportIncompatibleMethodOverride=false

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Queue

    @commands.hybrid_command(name="queue", aliases=["q"])
    @voice.is_queue_not_empty()
    @voice.is_player_connected()
    async def queue(self, ctx: custom.Context) -> None:
        """
        Shows the queue.
        """

        assert ctx.player is not None

        paginator = paginators.EmbedPaginator(
            ctx=ctx,
            entries=[
                f"**{index}. [{discord.utils.escape_markdown(track.title)}]({track.uri})** by **{discord.utils.escape_markdown(track.author or 'Unknown')}**\n"
                f"**⤷** {utilities.format_seconds(track.length // 1000, friendly=True)} | "
                f"{track.source.value.title()} | "
                f"Added by: {getattr(track.extras['ctx'].author, 'mention', None)}"
                for index, track in enumerate(ctx.player.queue, start=1)
            ],
            per_page=5,
            splitter="\n\n",
            embed_footer=f"{len(ctx.player.queue)} tracks | "
                         f"{utilities.format_seconds(sum(track.length for track in ctx.player.queue) // 1000, friendly=True)} | "
                         f"Loop mode: {ctx.player.queue.loop_mode.name.title()} | "
                         f"1 = up next",
        )
        await paginator.start()

    @commands.hybrid_command(name="history", aliases=["hist"])
    @voice.is_queue_history_not_empty()
    @voice.is_player_connected()
    async def history(self, ctx: custom.Context) -> None:
        """
        Shows the queue history.
        """

        assert ctx.player is not None

        paginator = paginators.EmbedPaginator(
            ctx=ctx,
            entries=[
                f"**{index}. [{discord.utils.escape_markdown(track.title)}]({track.uri})** by **{discord.utils.escape_markdown(track.author or 'Unknown')}**\n"
                f"**⤷** {utilities.format_seconds(track.length // 1000, friendly=True)} | "
                f"{track.source.value.title()} | "
                f"Added by: {getattr(track.extras['ctx'].author, 'mention', None)}"
                for index, track in enumerate(ctx.player.queue._history, start=1)
            ],
            per_page=5,
            splitter="\n\n",
            embed_footer=f"{len(ctx.player.queue._history)} tracks | "
                         f"{utilities.format_seconds(sum(track.length for track in ctx.player.queue._history) // 1000, friendly=True)} | "
                         f"Loop mode: {ctx.player.queue.loop_mode.name.title()} | "
                         f"1 = most recent",
        )
        await paginator.start()

    # General

    @commands.hybrid_command(name="clear", aliases=["clr"])
    @voice.is_queue_not_empty()
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def clear(self, ctx: custom.Context) -> None:
        """
        Clears the queue.
        """

        assert ctx.player is not None

        ctx.player.queue.clear()
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="Cleared the queue."
            )
        )
        await ctx.player.controller.update_current_message()

    @commands.hybrid_command(name="reverse")
    @voice.is_queue_not_empty()
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def reverse(self, ctx: custom.Context) -> None:
        """
        Reverses the queue.
        """

        assert ctx.player is not None

        ctx.player.queue.reverse()
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="Reversed the queue."
            )
        )
        await ctx.player.controller.update_current_message()

    @commands.hybrid_command(name="sort")
    @voice.is_queue_not_empty()
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def sort(
        self,
        ctx: custom.Context,
        method: Literal["title", "length", "author"],
        reverse: bool = False
    ) -> None:
        """
        Sorts the queue.

        **Arguments:**
        `method`: The method to sort by, can be one of the following:
        - `title`
        - `length`
        - `author`

        `reverse`: Whether to reverse the sorting order, can be one of the following:
        - `yes`/`y`/`true`/`t`/`on`
        - `no`/`n`/`false`/`f`/`off`
        """

        assert ctx.player is not None

        if method == "title":
            ctx.player.queue._items.sort(key=lambda track: track.title, reverse=reverse)
        elif method == "author":
            ctx.player.queue._items.sort(key=lambda track: track.author, reverse=reverse)
        elif method == "length":
            ctx.player.queue._items.sort(key=lambda track: track.length, reverse=reverse)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"{'Inversely sorted' if reverse else 'Sorted'} the queue with method **{method}**."
            )
        )
        await ctx.player.controller.update_current_message()

    @commands.hybrid_command(name="remove", aliases=["rm"])
    @voice.is_queue_not_empty()
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def remove(self, ctx: custom.Context, entry: int) -> None:
        """
        Removes a track from the queue.

        **Arguments:**
        `entry`: The position of the track to remove.
        """

        assert ctx.player is not None

        length = len(ctx.player.queue)

        if entry < 1 or entry > length:
            raise exceptions.EmbedError(
                description=f"**{utilities.truncate(entry, 10)}** is not a valid position, the queue only has "
                            f"**{length}** {utilities.pluralize('track', length)}."
            )

        track = ctx.player.queue.get_from_position(entry - 1, put_into_history=False)
        assert track is not None

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"Removed **[{discord.utils.escape_markdown(track.title)}]({track.uri})** "
                            f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}** from the queue."
            )
        )
        await ctx.player.controller.update_current_message()

    @commands.hybrid_command(name="move", aliases=["mv"])
    @voice.is_queue_not_empty()
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def move(self, ctx: custom.Context, entry: int, to: int) -> None:
        """
        Moves a track in the queue.

        **Arguments:**
        `entry`: The position of the track to move.
        `to`: The position to move the track to.
        """

        assert ctx.player is not None

        length = len(ctx.player.queue)

        if entry < 1 or entry > length:
            raise exceptions.EmbedError(
                description=f"**{utilities.truncate(entry, 10)}** is not a valid position, the queue only has "
                            f"**{length}** {utilities.pluralize('track', length)}."
            )
        if to < 1 or to > length:
            raise exceptions.EmbedError(
                description=f"**{utilities.truncate(to, 10)}** is not a valid position, the queue only has "
                            f"**{length}** {utilities.pluralize('track', length)}."
            )

        track = ctx.player.queue.get_from_position(entry - 1, put_into_history=False)
        assert track is not None

        ctx.player.queue.put_at_position(to - 1, item=track)
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"Moved **[{discord.utils.escape_markdown(track.title)}]({track.uri})** "
                            f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}** from position "
                            f"**{entry}** to position **{to}**.",
            )
        )
        await ctx.player.controller.update_current_message()

    @commands.hybrid_command(
        name="remove-duplicates",
        aliases=["remove_duplicates", "removeduplicates", "deduplicate", "dedupe"]
    )
    @voice.is_queue_not_empty()
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def remove_duplicates(self, ctx: custom.Context) -> None:
        """
        Removes duplicate tracks from the queue.
        """

        assert ctx.player is not None

        ctx.player.queue._items = list(
            {track.identifier: track for track in ctx.player.queue._items}.values()
        )

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="Removed duplicate tracks from the queue."
            )
        )
        await ctx.player.controller.update_current_message()

    # Toggleable

    @commands.hybrid_command(name="loop")
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def loop(self, ctx: custom.Context) -> None:
        """
        Switches between queue loop modes; disabled, current, and all.
        """

        assert ctx.player is not None

        match ctx.player.queue.loop_mode:
            case slate.QueueLoopMode.DISABLED:
                ctx.player.queue.set_loop_mode(slate.QueueLoopMode.ALL)
            case slate.QueueLoopMode.ALL:
                ctx.player.queue.set_loop_mode(slate.QueueLoopMode.CURRENT)
            case slate.QueueLoopMode.CURRENT:
                ctx.player.queue.set_loop_mode(slate.QueueLoopMode.DISABLED)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"The queue loop mode is now **{ctx.player.queue.loop_mode.name.title()}**.",
            )
        )
        await ctx.player.controller.update_current_message()

    @commands.hybrid_command(name="shuffle")
    @voice.is_author_connected()
    @voice.is_player_connected()
    async def shuffle(self, ctx: custom.Context) -> None:
        """
        Toggles the queue shuffling or not.
        """

        assert ctx.player is not None

        match ctx.player.queue.shuffle_state:
            case True:
                ctx.player.queue.set_shuffle_state(False)
                description = "The queue will no longer shuffle."
            case False:
                ctx.player.queue.set_shuffle_state(True)
                description = "The queue will now shuffle."
            case _:
                raise ValueError

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=description
            )
        )
        await ctx.player.controller.update_current_message()
