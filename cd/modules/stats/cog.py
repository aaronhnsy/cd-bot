from discord.ext import commands, paginators

from cd import custom


__all__ = ["Stats"]


class Stats(custom.Cog, name="Stats"):
    emoji = "📊"
    description = "Commands for tracking and displaying bot statistics."

    @custom.Cog.listener("on_socket_event_type")
    async def track_socket_events(self, event_type: str) -> None:
        self.bot.socket_stats[event_type] += 1

    @custom.Cog.listener("on_command")
    async def track_total_commands(self, ctx: custom.Context) -> None:
        if ctx.command is None:
            return
        self.bot.command_stats["total"][ctx.command.qualified_name] += 1

    @custom.Cog.listener("on_command_completion")
    async def track_successful_commands(self, ctx: custom.Context) -> None:
        if ctx.command is None:
            return
        self.bot.command_stats["successful"][ctx.command.qualified_name] += 1

    @custom.Cog.listener("on_command_error")
    async def track_failed_commands(self, ctx: custom.Context, _: Exception) -> None:
        if ctx.command is None:
            return
        self.bot.command_stats["failed"][ctx.command.qualified_name] += 1

    @commands.command(name="socket-stats", aliases=["socket_stats", "ss"])
    async def socket_stats(self, ctx: custom.Context) -> None:
        """Display the bot's socket event statistics."""
        # calculate 'event' column width
        event_column_width = max(map(len, self.bot.socket_stats.keys()))
        event_column_bar = "═" * event_column_width
        # calculate 'count' column width
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
