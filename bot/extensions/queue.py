# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
from discord.ext import commands

# My stuff
from core import values
from core.bot import CD
from utilities import checks, custom, exceptions, utils


def setup(bot: CD) -> None:
    bot.add_cog(Queue(bot))


class Queue(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    def cog_check(self, ctx: commands.Context) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    # Queue

    @commands.group(name="queue", aliases=["q"])
    @checks.is_queue_not_empty()
    @checks.is_player_connected()
    async def queue(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        await ctx.paginate_embed(
            entries=[
                f"**{index + 1}.** [{track.title}]({track.uri}) | {utils.format_seconds(track.length // 1000)} | {getattr(track.requester, 'mention', None)}"
                for index, track in enumerate(ctx.voice_client.queue)
            ],
            per_page=10,
            title="Queue:",
            header=f"**Tracks:** {len(ctx.voice_client.queue)}\n"
                   f"**Time:** {utils.format_seconds(sum(track.length for track in ctx.voice_client.queue) // 1000, friendly=True)}\n"
                   f"**Loop mode:** {ctx.voice_client.queue.loop_mode.name.title()}\n\n",
        )

    @commands.command(name="queue-detailed", aliases=["queue_detailed", "queuedetailed", "qd"])
    @checks.is_queue_not_empty()
    @checks.is_player_connected()
    async def queue_detailed(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        entries = []

        for track in ctx.voice_client.queue:

            embed = utils.embed(
                colour=values.MAIN,
                title=track.title,
                url=track.uri,
                description=f"**Author:** {track.author}\n"
                            f"**Length:** {utils.format_seconds(round(track.length) // 1000, friendly=True)}\n"
                            f"**Source:** {track.source.name.title()}\n"
                            f"**Requester:** {getattr(track.requester, 'mention', None)} `{getattr(track.requester, 'id', None)}`\n"
                            f"**Is stream:** {track.is_stream()}\n"
                            f"**Is seekable:** {track.is_seekable()}\n",
                image=track.thumbnail
            )
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    # Queue history

    @commands.command(name="queue-history", aliases=["queue_history", "queuehistory", "qh"])
    @checks.is_queue_history_not_empty()
    @checks.is_player_connected()
    async def queue_history(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        await ctx.paginate_embed(
            entries=[
                f"**{index + 1}.** [{track.title}]({track.uri}) | {utils.format_seconds(track.length // 1000)} | {getattr(track.requester, 'mention', None)}"
                for index, track in enumerate(ctx.voice_client.queue._history)
            ],
            per_page=10,
            title="Queue history:",
            header=f"**Tracks:** {len(ctx.voice_client.queue._history)}\n"
                   f"**Time:** {utils.format_seconds(sum(track.length for track in ctx.voice_client.queue._history) // 1000, friendly=True)}\n\n",
            embed_footer=f"1 = most recent | {len(ctx.voice_client.queue._history)} = least recent",
        )

    @commands.command(name="queue-history-detailed", aliases=["queue_history_detailed", "queuehistorydetailed", "qhd"])
    @checks.is_queue_history_not_empty()
    @checks.is_player_connected()
    async def queue_history_detailed(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        entries = []

        for track in ctx.voice_client.queue._history:

            embed = utils.embed(
                title=track.title,
                url=track.uri,
                description=f"**Author:** {track.author}\n"
                            f"**Length:** {utils.format_seconds(round(track.length) // 1000, friendly=True)}\n"
                            f"**Source:** {track.source.name.title()}\n"
                            f"**Requester:** {getattr(track.requester, 'mention', None)} `{getattr(track.requester, 'id', None)}`\n"
                            f"**Is stream:** {track.is_stream()}\n"
                            f"**Is seekable:** {track.is_seekable()}\n",
                image=track.thumbnail,
                footer=f"1 = most recent | {len(ctx.voice_client.queue._history)} = least recent"
            )
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    # Queue control commands

    @commands.command(name="clear", aliases=["clr"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def clear(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        ctx.voice_client.queue.clear()
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="The queue has been cleared."
            )
        )

    @commands.command(name="shuffle", aliases=["shfl"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def shuffle(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        ctx.voice_client.queue.shuffle()
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="The queue has been shuffled."
            )
        )

    @commands.command(name="reverse")
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def reverse(self, ctx: custom.Context) -> None:

        assert ctx.voice_client is not None

        ctx.voice_client.queue.reverse()
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="The queue has been reversed."
            )
        )

    @commands.command(name="sort")
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def sort(self, ctx: custom.Context, method: Literal["title", "length", "author"], reverse: bool = False) -> None:

        assert ctx.voice_client is not None

        if method == "title":
            ctx.voice_client.queue._queue.sort(key=lambda track: track.title, reverse=reverse)
        elif method == "author":
            ctx.voice_client.queue._queue.sort(key=lambda track: track.author, reverse=reverse)
        elif method == "length":
            ctx.voice_client.queue._queue.sort(key=lambda track: track.length, reverse=reverse)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"The queue has been sorted by**{method}**."
            )
        )

    @commands.command(name="remove", aliases=["rm"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def remove(self, ctx: custom.Context, entry: int = 0) -> None:

        assert ctx.voice_client is not None

        if entry <= 0 or entry > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                description=f"That was not a valid track entry, try again with a number between **1** and **{len(ctx.voice_client.queue)}**.",
            )

        track = ctx.voice_client.queue.get(entry - 1, put_history=False)
        assert track is not None

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Removed **[{track.title}]({track.uri})** by **{track.author}** from the queue."
            )
        )

    @commands.command(name="move", aliases=["mv"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def move(self, ctx: custom.Context, entry_1: int = 0, entry_2: int = 0) -> None:

        assert ctx.voice_client is not None

        if entry_1 <= 0 or entry_1 > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                description=f"That was not a valid track entry to move from, try again with a number between **1** and **{len(ctx.voice_client.queue)}**.",
            )
        if entry_2 <= 0 or entry_2 > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                description=f"That was not a valid track entry to move too, try again with a number between **1** and **{len(ctx.voice_client.queue)}**.",
            )

        track = ctx.voice_client.queue.get(entry_1 - 1, put_history=False)
        assert track is not None

        ctx.voice_client.queue.put(track, position=entry_2 - 1)
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"Moved **[{track.title}]({track.uri})** by **{track.author}** from position **{entry_1}** to position **{entry_2}**.",
            )
        )
