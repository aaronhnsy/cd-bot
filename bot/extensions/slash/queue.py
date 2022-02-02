# Future
from __future__ import annotations

# Standard Library
from typing import Literal

# Packages
import discord
import slate

# My stuff
from core import values
from core.bot import CD
from utilities import checks, exceptions, paginators, slash, utils


def setup(bot: CD) -> None:
    bot.add_cog(SlashQueue(bot))


class SlashQueue(slash.ApplicationCog):

    # Queue

    @slash.slash_command(name="queue", guild_id=240958773122957312)
    @checks.is_queue_not_empty()
    @checks.is_player_connected()
    async def queue(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        paginator = paginators.EmbedPaginator(
            ctx=ctx,
            entries=[
                f"**{index + 1}. [{discord.utils.escape_markdown(track.title)}]({track.uri})** by **{discord.utils.escape_markdown(track.author or 'Unknown')}**\n"
                f"**⤷** {utils.format_seconds(track.length // 1000, friendly=True)} | "
                f"{track.source.value.title()} | "
                f"Added by: {getattr(track.requester, 'mention', None)}"
                for index, track in enumerate(ctx.voice_client.queue._queue)
            ],
            per_page=5,
            splitter="\n\n",
            embed_footer=f"{len(ctx.voice_client.queue._queue)} tracks | "
                         f"{utils.format_seconds(sum(track.length for track in ctx.voice_client.queue._queue) // 1000, friendly=True)} | "
                         f"Loop mode: {ctx.voice_client.queue.loop_mode.name.title()} | "
                         f"1 = up next",
        )
        await paginator.start()

    @slash.slash_command(name="queue-history", guild_id=240958773122957312)
    @checks.is_queue_history_not_empty()
    @checks.is_player_connected()
    async def queue_history(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        paginator = paginators.EmbedPaginator(
            ctx=ctx,
            entries=[
                f"**{index + 1}. [{discord.utils.escape_markdown(track.title)}]({track.uri})** by **{discord.utils.escape_markdown(track.author or 'Unknown')}**\n"
                f"**⤷** {utils.format_seconds(track.length // 1000, friendly=True)} | "
                f"{track.source.value.title()} | "
                f"Added by: {getattr(track.requester, 'mention', None)}"
                for index, track in enumerate(reversed(ctx.voice_client.queue._history))
            ],
            per_page=5,
            splitter="\n\n",
            embed_footer=f"{len(ctx.voice_client.queue._history)} tracks | "
                         f"{utils.format_seconds(sum(track.length for track in ctx.voice_client.queue._history) // 1000, friendly=True)} | "
                         f"Loop mode: {ctx.voice_client.queue.loop_mode.name.title()} | "
                         f"1 = most recent",
        )
        await paginator.start()

    # General

    @slash.slash_command(name="clear-queue", guild_id=240958773122957312)
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def clear_queue(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        ctx.voice_client.queue.clear()
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**cleared** the queue."
            )
        )

    @slash.slash_command(name="shuffle-queue", guild_id=240958773122957312)
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def shuffle_queue(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        ctx.voice_client.queue.shuffle()
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**shuffled** the queue."
            )
        )

    @slash.slash_command(name="reverse-queue", guild_id=240958773122957312)
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def reverse_queue(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        ctx.voice_client.queue.reverse()
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**reversed** the queue."
            )
        )

    @slash.slash_command(name="sort-queue", guild_id=240958773122957312)
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def sort_queue(self, ctx: slash.ApplicationContext, method: Literal["title", "length", "author"], reverse: bool = False) -> None:

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
                description=f"**{'inversely sorted' if reverse else 'sorted'}** the queue by **{method}**."
            )
        )

    @slash.slash_command(name="remove-entry", guild_id=240958773122957312)
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def remove(self, ctx: slash.ApplicationContext, entry: int) -> None:

        assert ctx.voice_client is not None

        if entry <= 0 or entry > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                description=f"**{entry}** is not a valid queue position, the queue only has "
                            f"**{len(ctx.voice_client.queue)}** track{'s' if len(ctx.voice_client.queue) > 1 else ''}.",
            )

        track = ctx.voice_client.queue.get(entry - 1, put_history=False)
        assert track is not None

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"removed **{entry}. [{discord.utils.escape_markdown(track.title)}]({track.uri})** "
                            f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}** from the queue."
            )
        )

    @slash.slash_command(name="move-entry", guild_id=240958773122957312)
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def move(self, ctx: slash.ApplicationContext, entry: int, to: int) -> None:

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
        assert track

        ctx.voice_client.queue.put(track, position=to - 1)
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"moved **{entry}. [{discord.utils.escape_markdown(track.title)}]({track.uri})** "
                            f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}** from position **{entry}** to position **{to}**.",
            )
        )

    @slash.slash_command(name="delete-duplicates", guild_id=240958773122957312)
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def delete_duplicates(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        ctx.voice_client.queue._queue = list({track.identifier: track for track in ctx.voice_client.queue._queue}.values())
        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description="**removed duplicate tracks** from the queue."
            )
        )

    # Looping

    @slash.slash_command(name="loop-current", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def loop_current(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if ctx.voice_client.queue.loop_mode != slate.QueueLoopMode.CURRENT:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.CURRENT)
        else:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.OFF)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"queue loop mode is now **{ctx.voice_client.queue.loop_mode.name.title()}**.",
            )
        )

    @slash.slash_command(name="loop-queue", guild_id=240958773122957312)
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def loop_queue(self, ctx: slash.ApplicationContext) -> None:

        assert ctx.voice_client is not None

        if ctx.voice_client.queue.loop_mode != slate.QueueLoopMode.QUEUE:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.QUEUE)
        else:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.OFF)

        await ctx.reply(
            embed=utils.embed(
                colour=values.GREEN,
                description=f"queue loop mode is now **{ctx.voice_client.queue.loop_mode.name.title()}**.",
            )
        )
