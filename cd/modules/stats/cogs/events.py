# Project
from cd import custom


__all__ = ["StatsEvents"]


class StatsEvents(custom.Cog):

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
