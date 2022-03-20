# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import discord
import slate
from discord.ext import commands

# My stuff
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
                f"**{index + 1}. [{discord.utils.escape_markdown(track.title)}]({track.uri})** by **{discord.utils.escape_markdown(track.author or 'Unknown')}**\n"
                f"**⤷** {utilities.format_seconds(track.length // 1000, friendly=True)} | "
                f"{track.source.value.title()} | "
                f"Added by: {getattr(track.requester, 'mention', None)}"
                for index, track in enumerate(ctx.voice_client.queue._queue)
            ],
            per_page=5,
            splitter="\n\n",
            embed_footer=f"{len(ctx.voice_client.queue._queue)} tracks | "
                         f"{utilities.format_seconds(sum(track.length for track in ctx.voice_client.queue._queue) // 1000, friendly=True)} | "
                         f"Loop mode: {ctx.voice_client.queue.loop_mode.name.title()} | "
                         f"1 = up next",
        )
        await paginator.start()

    @commands.command(name="queue-history", aliases=["queue_history", "queuehistory", "qh"])
    @checks.is_queue_history_not_empty()
    @checks.is_player_connected()
    async def queue_history(self, ctx: custom.Context) -> None:
        """
        Shows the queue history.
        """

        assert ctx.voice_client is not None

        paginator = paginators.EmbedPaginator(
            ctx=ctx,
            entries=[
                f"**{index + 1}. [{discord.utils.escape_markdown(track.title)}]({track.uri})** by **{discord.utils.escape_markdown(track.author or 'Unknown')}**\n"
                f"**⤷** {utilities.format_seconds(track.length // 1000, friendly=True)} | "
                f"{track.source.value.title()} | "
                f"Added by: {getattr(track.requester, 'mention', None)}"
                for index, track in enumerate(reversed(ctx.voice_client.queue._history))
            ],
            per_page=5,
            splitter="\n\n",
            embed_footer=f"{len(ctx.voice_client.queue._history)} tracks | "
                         f"{utilities.format_seconds(sum(track.length for track in ctx.voice_client.queue._history) // 1000, friendly=True)} | "
                         f"Loop mode: {ctx.voice_client.queue.loop_mode.name.title()} | "
                         f"1 = most recent",
        )
        await paginator.start()

    # General

    @commands.command(name="clear")
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

    @commands.command(name="shuffle")
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def shuffle(self, ctx: custom.Context) -> None:
        """
        Shuffles the queue.
        """

        assert ctx.voice_client is not None

        ctx.voice_client.queue.shuffle()
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="**Shuffled** the queue."
            )
        )

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

        `reverse`: Whether to reverse the order, can be one of the following:
        - `true`
        - `false`
        - `on`
        - `off`
        - `yes`
        - `no`
        """

        assert ctx.voice_client is not None

        if method == "title":
            ctx.voice_client.queue._queue.sort(key=lambda track: track.title, reverse=reverse)
        elif method == "author":
            ctx.voice_client.queue._queue.sort(key=lambda track: track.author, reverse=reverse)
        elif method == "length":
            ctx.voice_client.queue._queue.sort(key=lambda track: track.length, reverse=reverse)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"**{'Inversely sorted' if reverse else 'Sorted'}** the queue by **{method}**."
            )
        )

    @commands.command(name="remove", aliases=["rm"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def remove(self, ctx: custom.Context, entry: int = 0) -> None:
        """
        Removes a track from the queue.

        **Arguments:**
        `entry`: The index of the track to remove.
        """

        assert ctx.voice_client is not None

        if entry <= 0 or entry > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                description=f"**{entry}** is not a valid queue position, the queue only has "
                            f"**{len(ctx.voice_client.queue)}** track{'s' if len(ctx.voice_client.queue) > 1 else ''}.",
            )

        track = ctx.voice_client.queue.get(entry - 1, put_history=False)
        assert track is not None

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"Removed **{entry}. [{discord.utils.escape_markdown(track.title)}]({track.uri})** "
                            f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}** from the queue."
            )
        )

    @commands.command(name="move", aliases=["mv"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def move(self, ctx: custom.Context, entry: int = 0, to: int = 0) -> None:
        """
        Moves a track in the queue.

        **Arguments:**
        `entry`: The index of the track to move.
        `to`: The index to move the track to.
        """

        assert ctx.voice_client is not None

        if entry <= 0 or entry > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                description=f"**{entry}** is not a valid queue position, the queue only has "
                            f"**{len(ctx.voice_client.queue)}** track{'s' if len(ctx.voice_client.queue) > 1 else ''}.",
            )
        if to <= 0 or to > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                description=f"**{to}** is not a valid queue position, the queue only has "
                            f"**{len(ctx.voice_client.queue)}** track{'s' if len(ctx.voice_client.queue) > 1 else ''}.",
            )

        track = ctx.voice_client.queue.get(entry - 1, put_history=False)
        assert track is not None

        ctx.voice_client.queue.put(track, position=to - 1)
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"Moved **[{discord.utils.escape_markdown(track.title)}]({track.uri})** "
                            f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}** from position **{entry}** to position **{to}**.",
            )
        )

    @commands.command(name="remove-duplicates", aliases=["remove_duplicates", "removeduplicates", "deduplicate", "dedupe"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def remove_duplicates(self, ctx: custom.Context) -> None:
        """
        Removes duplicate tracks from the queue.
        """

        assert ctx.voice_client is not None

        ctx.voice_client.queue._queue = list({track.identifier: track for track in ctx.voice_client.queue._queue}.values())
        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description="**Removed** duplicate tracks from the queue."
            )
        )

    # Looping

    @staticmethod
    async def _change_queue_loop_mode(ctx: custom.Context, *, current: bool) -> None:

        assert ctx.voice_client is not None

        mode = slate.QueueLoopMode.CURRENT if current else slate.QueueLoopMode.QUEUE

        if ctx.voice_client.queue.loop_mode != mode:
            ctx.voice_client.queue.set_loop_mode(mode)
        else:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.OFF)

        await ctx.reply(
            embed=utilities.embed(
                colour=values.GREEN,
                description=f"**Set** the queue loop mode to **{ctx.voice_client.queue.loop_mode.name.title()}**.",
            )
        )

    @commands.command(name="loop-current", aliases=["loop_current", "loopcurrent", "loopc", "cloop"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def loop_current(self, ctx: custom.Context) -> None:
        """
        Loops the current track.
        """
        await self._change_queue_loop_mode(ctx, current=True)

    @commands.command(name="loop-queue", aliases=["loop_queue", "loopqueue", "loopq", "qloop", "loop"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def loop_queue(self, ctx: custom.Context) -> None:
        """
        Loops the entire queue.
        """
        await self._change_queue_loop_mode(ctx, current=False)
