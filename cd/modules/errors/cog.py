import discord.utils
from discord.ext import commands

from cd import custom, enums, exceptions, utilities, values
from cd.modules.errors.handlers import ERROR_HANDLERS, command_not_found, original


__all__ = ["Errors"]


class Errors(custom.Cog, name="Errors"):
    emoji = "🚫"
    description = "Error handling and testing commands."

    @staticmethod
    def _build_error_webhook_embed(ctx: custom.Context, error: commands.CommandError) -> discord.Embed:
        user_info = (f"[**User**](https://discord.com/users/{ctx.author.id}):\n"
                     f"- **ID:** {ctx.author.id}\n"
                     f"- **Name:** {ctx.author.display_name} ({ctx.author.global_name})\n")
        guild_info = (f"[**Guild**](https://discord.com/channels/{ctx.guild.id}):\n"
                      f"- **ID:** {ctx.guild.id}\n"
                      f"- **Name:** {ctx.guild}\n") if ctx.guild else ""
        channel_info = (f"[**Channel**]({ctx.channel.jump_url}):\n"
                        f"- **ID:** {ctx.channel.id}\n"
                        f"- **Name:** {ctx.channel}\n")
        message_info = (f"[**Message**]({ctx.message.jump_url}):\n"
                        f"- **ID:** {ctx.message.id}\n"
                        f"- **Sent at:** {utilities.format_date_and_or_time(
                            ctx.message.created_at,
                            format=enums.DateTimeFormat.DATE_WITH_TIME_AND_SECONDS,
                            timezone_format="zz",
                        )}\n")
        return utilities.embed(
            colour=values.ERROR_COLOUR,
            title=f"{type(error).__name__}: {ctx.command.qualified_name if ctx.command else "Unknown"}",
            description=f"{user_info}{guild_info}{channel_info}{message_info}",
        )

    @custom.Cog.listener("on_command_error")
    async def on_command_error(self, ctx: custom.Context, error: commands.CommandError) -> None:
        if isinstance(error, exceptions.EmbedError):
            await ctx.reply(
                embed=error.embed,
                view=error.view or discord.utils.MISSING,
            )
            return
        # log the error to the webhook provided in the config
        await self.bot.webhooks["errors"].send(
            content=utilities.codeblock(utilities.format_traceback(error), language="py"),
            embed=self._build_error_webhook_embed(ctx, error),
        )
        # show a user-friendly error message depending on its type
        if (error_handler := ERROR_HANDLERS.get(type(error))) is not None:
            response = error_handler(error, ctx)
            await ctx.reply(
                embed=utilities.embed(
                    colour=values.ERROR_COLOUR,
                    description=response.description,
                    footer=response.footer,
                )
            )
        elif isinstance(error, commands.CommandNotFound):
            await command_not_found(error, ctx)
        elif isinstance(error, commands.ConversionError | commands.CommandInvokeError | commands.HybridCommandError):
            await original(error.original, ctx)
        else:
            await original(error, ctx)

    @commands.command(name="error")
    async def error(self, ctx: custom.Context) -> None:
        """Raises an error to test the error handler."""
        raise ValueError("This is a test error.")
