# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import discord
import slate
from discord.ext import commands

# Local
from cd import checks, custom, exceptions, paginators, utilities, values
from cd.bot import CD


async def setup(bot: CD) -> None:
    await bot.add_cog(Queue(bot))


class Queue(commands.Cog):
    """
    Queue management commands.
    """

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: custom.Context) -> Literal[True]:  # pyright: reportIncompatibleMethodOverride=false

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Queue

    @commands.group(name="queue", aliases=["q"])
    @checks.is_queue_not_empty()
    @checks.is_player_connected()
    async def queue(self, ctx: custom.Context) -> None:
        """
        Shows the queue.
        """

        assert ctx.voice_client is not None

        paginator = paginators.EmbedPaginator(
            ctx=ctx,
            entries=[
                f"**{index}. [{discord.utils.escape_markdown(item.track.title)}]({item.track.uri})** by **{discord.utils.escape_markdown(item.track.author or 'Unknown')}**\n"
                f"**⤷** {utilities.format_seconds(item.track.length // 1000, friendly=True)} | "
                f"{item.track.source.value.title()} | "
                f"Added by: {getattr(item.track.requester, 'mention', None)}"
                for index, item in enumerate(ctx.voice_client.queue.items, start=1)
            ],
            per_page=5,
            splitter="\n\n",
            embed_footer=f"{len(ctx.voice_client.queue.items)} tracks | "
                         f"{utilities.format_seconds(sum(item.track.length for item in ctx.voice_client.queue.items) // 1000, friendly=True)} | "
                         f"Loop mode: {ctx.voice_client.queue.loop_mode.name.title()} | "
                         f"1 = up next",
        )
        await paginator.start()

    @commands.command(name="history", aliases=["hist"])
    @checks.is_queue_history_not_empty()
    @checks.is_player_connected()
    async def history(self, ctx: custom.Context) -> None:
        """
        Shows the queue history.
        """

        assert ctx.voice_client is not None

        paginator = paginators.EmbedPaginator(
            ctx=ctx,
            entries=[
                f"**{index}. [{discord.utils.escape_markdown(track.title)}]({track.uri})** by **{discord.utils.escape_markdown(track.author or 'Unknown')}**\n"
                f"**⤷** {utilities.format_seconds(track.length // 1000, friendly=True)} | "
                f"{track.source.value.title()} | "
                f"Added by: {getattr(track.requester, 'mention', None)}"
                for index, track in enumerate(ctx.voice_client.queue.history, start=1)
            ],
            per_page=5,
            splitter="\n\n",
            embed_footer=f"{len(ctx.voice_client.queue.history)} tracks | "
                         f"{utilities.format_seconds(sum(track.length for track in ctx.voice_client.queue.history) // 1000, friendly=True)} | "
                         f"Loop mode: {ctx.voice_client.queue.loop_mode.name.title()} | "
                         f"1 = most recent",
        )
        await paginator.start()

    # General

    @commands.command(name="clear", aliases=["clr"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def clear(self, ctx: custom.Context) -> None:
        """
        Clears the queue.
        """

        assert ctx.voice_client is not None

        ctx.voice_client.queue.clear()
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="**Cleared** the queue."
            )
        )
        await ctx.voice_client.controller.update_current_message()

    @commands.command(name="reverse")
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def reverse(self, ctx: custom.Context) -> None:
        """
        Reverses the queue.
        """

        assert ctx.voice_client is not None

        ctx.voice_client.queue.reverse()
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="**Reversed** the queue."
            )
        )
        await ctx.voice_client.controller.update_current_message()

    @commands.command(name="sort")
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def sort(self, ctx: custom.Context, method: Literal["title", "length", "author"], reverse: bool = False) -> None:
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

        assert ctx.voice_client is not None

        if method == "title":
            ctx.voice_client.queue.items.sort(key=lambda item: item.track.title, reverse=reverse)
        elif method == "author":
            ctx.voice_client.queue.items.sort(key=lambda item: item.track.author, reverse=reverse)
        elif method == "length":
            ctx.voice_client.queue.items.sort(key=lambda item: item.track.length, reverse=reverse)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"**{'Inversely sorted' if reverse else 'Sorted'}** the queue with method **track {method}**."
            )
        )
        await ctx.voice_client.controller.update_current_message()

    @commands.command(name="remove", aliases=["rm"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def remove(self, ctx: custom.Context, entry: int = 0) -> None:
        """
        Removes a track from the queue.

        **Arguments:**
        `entry`: The position of the track to remove.
        """

        assert ctx.voice_client is not None

        length = len(ctx.voice_client.queue)

        if entry < 1 or entry > length:
            raise exceptions.EmbedError(
                description=f"**{utilities.truncate(entry, 10)}** is not a valid position, the queue only has "
                            f"**{length}** {utilities.pluralize('track', length)}."
            )

        item = ctx.voice_client.queue.get(position=entry - 1)
        assert item is not None

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"Removed **[{discord.utils.escape_markdown(item.track.title)}]({item.track.uri})** "
                            f"by **{discord.utils.escape_markdown(item.track.author or 'Unknown')}** from the queue."
            )
        )
        await ctx.voice_client.controller.update_current_message()

    @commands.command(name="move", aliases=["mv"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def move(self, ctx: custom.Context, entry: int = 0, to: int = 0) -> None:
        """
        Moves a track in the queue.

        **Arguments:**
        `entry`: The position of the track to move.
        `to`: The position to move the track to.
        """

        assert ctx.voice_client is not None

        length = len(ctx.voice_client.queue)

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

        item = ctx.voice_client.queue.get(position=entry - 1)
        assert item is not None

        ctx.voice_client.queue.put(item, position=to - 1)
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"Moved **[{discord.utils.escape_markdown(item.track.title)}]({item.track.uri})** "
                            f"by **{discord.utils.escape_markdown(item.track.author or 'Unknown')}** from position "
                            f"**{entry}** to position **{to}**.",
            )
        )
        await ctx.voice_client.controller.update_current_message()

    @commands.command(name="remove-duplicates", aliases=["remove_duplicates", "removeduplicates", "deduplicate", "dedupe"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def remove_duplicates(self, ctx: custom.Context) -> None:
        """
        Removes duplicate tracks from the queue.
        """

        assert ctx.voice_client is not None

        ctx.voice_client.queue.items = list({item.track.identifier: item for item in ctx.voice_client.queue.items}.values())
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="**Removed** duplicate tracks from the queue."
            )
        )
        await ctx.voice_client.controller.update_current_message()

    # Toggleable

    @commands.command(name="loop")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def loop(self, ctx: custom.Context) -> None:
        """
        Switches between queue loop modes; disabled, current, and all.
        """

        assert ctx.voice_client is not None

        match ctx.voice_client.queue.loop_mode:
            case slate.QueueLoopMode.DISABLED:
                ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.ALL)
            case slate.QueueLoopMode.ALL:
                ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.CURRENT)
            case slate.QueueLoopMode.CURRENT:
                ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.DISABLED)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"The queue loop mode is now **{ctx.voice_client.queue.loop_mode.name.title()}**.",
            )
        )
        await ctx.voice_client.controller.update_current_message()

    @commands.command(name="shuffle")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def shuffle(self, ctx: custom.Context) -> None:
        """
        Toggles the queue shuffling or not.
        """

        assert ctx.voice_client is not None

        match ctx.voice_client.queue.shuffle_state:
            case True:
                ctx.voice_client.queue.set_shuffle_state(True)
                description = "The queue will now shuffle."
            case False:
                ctx.voice_client.queue.set_shuffle_state(False)
                description = "The queue will no longer shuffle."
            case _:
                raise ValueError

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=description
            )
        )
        await ctx.voice_client.controller.update_current_message()
