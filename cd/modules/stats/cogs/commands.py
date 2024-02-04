from discord.ext import commands, paginators

from cd import custom


__all__ = ["StatsCommands"]


class StatsCommands(custom.Cog, name="Stats"):

    @commands.command(name="socket-stats", aliases=["socket_stats", "ss"])
    async def socket_stats(self, ctx: custom.Context) -> None:
        # calculate event column width
        event_column_width = max(map(len, self.bot.socket_stats.keys()))
        event_column_bar = "═" * event_column_width
        # calculate count column width
        count_column_width = max(5, max(map(len, map(str, self.bot.socket_stats.values()))))
        count_column_bar = "═" * count_column_width
        # format the items, header, and footer for the table
        items = [
            f"║ {event:^{event_column_width}} ║ {count:>{count_column_width}} ║"
            for event, count in sorted(self.bot.socket_stats.items(), key=lambda x: x[1], reverse=True)
        ]
        header = f"╔═{event_column_bar}═╦═{count_column_bar}═╗\n" \
                 f"║ {"Event":^{event_column_width}} ║ {"Count":^{count_column_width}} ║\n" \
                 f"╠═{event_column_bar}═╬═{count_column_bar}═╣"
        footer = f"╚═{event_column_bar}═╩═{count_column_bar}═╝"
        # paginate the events and their counts
        await paginators.TextPaginator(
            ctx=ctx,
            items=items,
            items_per_page=20,
            controller=custom.PaginatorController,
            header=header,
            footer=footer,
            codeblock_type=paginators.CodeblockType.BLOCK
        ).start()
