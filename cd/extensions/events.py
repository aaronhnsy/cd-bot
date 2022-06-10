# Future
from __future__ import annotations

# Standard Library
import asyncio
import logging
import traceback

# Packages
import discord
import pendulum
import slate
from discord.ext import commands

# Local
from cd import config, custom, enums, exceptions, utilities, values
from cd.bot import CD


__log__: logging.Logger = logging.getLogger("extensions.events")


COOLDOWN_BUCKETS = {
    commands.BucketType.default:  "for the whole bot",
    commands.BucketType.user:     "for you",
    commands.BucketType.member:   "for you",
    commands.BucketType.role:     "for your role",
    commands.BucketType.guild:    "for this server",
    commands.BucketType.channel:  "for this channel",
    commands.BucketType.category: "for this channel category",
}

CONCURRENCY_BUCKETS = {
    commands.BucketType.default:  "for all users",
    commands.BucketType.user:     "per user",
    commands.BucketType.member:   "per member",
    commands.BucketType.role:     "per role",
    commands.BucketType.guild:    "per server",
    commands.BucketType.channel:  "per channel",
    commands.BucketType.category: "per channel category",
}

ERRORS: dict[type[commands.CommandError], str] = {
    commands.MissingRequiredArgument:       "You missed the **{error.param.name}** argument.",
    commands.TooManyArguments:              "You used too many arguments for this command.",
    commands.BadUnionArgument:              "I couldn't convert your **{error.param.name}** argument into any of the accepted types.",

    commands.UnexpectedQuoteError:          "There was an unexpected quote mark in your input.",
    commands.InvalidEndOfQuotedStringError: "There was an unexpected character after a quote mark in your input.",
    commands.ExpectedClosingQuoteError:     "There is a missing quote mark in your input.",

    commands.CheckFailure:                  "You are not able to use this command.",
    commands.CheckAnyFailure:               "You are not able to use this command.",
    commands.PrivateMessageOnly:            "This command can only be used in DM's.",
    commands.NoPrivateMessage:              "This command can not be used in DM's.",
    commands.NotOwner:                      "You don't have permission to use this command.",
    commands.NSFWChannelRequired:           "This command can only be used in NSFW channels.",
    commands.DisabledCommand:               "This command is disabled.",

    commands.BadArgument:                   "I couldn't convert one of the arguments you used.",
    commands.MessageNotFound:               "I couldn't find a message that matches **{error.argument}**.",
    commands.MemberNotFound:                "I couldn't find a member that matches **{error.argument}**.",
    commands.GuildNotFound:                 "I couldn't find a server that matches **{error.argument}**.",
    commands.UserNotFound:                  "I couldn't find a user that matches **{error.argument}**.",
    commands.ChannelNotFound:               "I couldn't find a channel that matches **{error.argument}**.",
    commands.RoleNotFound:                  "I couldn't find a role that matches **{error.argument}**.",
    commands.BadColourArgument:             "I couldn't find a colour that matches **{error.argument}**.",
    commands.EmojiNotFound:                 "I couldn't find an emoji that matches **{error.argument}**.",
    commands.ThreadNotFound:                "I couldn't find a thread that matches **{error.argument}**.",
    commands.GuildStickerNotFound:          "I couldn't find a sticker that matches **{error.argument}**.",

    commands.ChannelNotReadable:            "I don't have permission to read messages in **{error.argument.mention}**.",
    commands.BadInviteArgument:             "**{error.argument}** is not a valid invite.",
    commands.PartialEmojiConversionFailure: "**{error.argument}** does not match the emoji format.",
    commands.BadBoolArgument:               "**{error.argument}** is not a valid true or false value.",

    commands.BadFlagArgument:               "I couldn't convert a value for the **{error.flag.name}** flag.",
    commands.MissingFlagArgument:           "You missed a value for the **{error.flag.name}** flag.",
    commands.TooManyFlags:                  "You gave too many values for the **{error.flag.name}** flag.",
    commands.MissingRequiredFlag:           "You missed the **{error.flag.name}** flag.",
}

NL = "\n"


async def setup(bot: CD) -> None:
    await bot.add_cog(Events(bot))


class Events(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    @staticmethod
    async def _build_command_information_embed(ctx: custom.Context, colour: discord.Colour) -> discord.Embed:

        assert ctx.command is not None

        if ctx.guild:
            guild_info = f"**● [Guild:]({utilities.guild_url(ctx.guild.id)})**\n" \
                         f"{values.NQSP * 2}**● Name:** {ctx.guild}\n" \
                         f"{values.NQSP * 2}**● ID:** `{ctx.guild.id}`\n"
        else:
            guild_info = ""

        now = ctx.message.created_at or pendulum.now(tz="UTC")

        return utilities.embed(
            colour=colour,
            title=f"{ctx.prefix}{ctx.command.qualified_name}",
            description=f"{await utilities.upload_text(ctx.bot.mystbin, content=ctx.message.content, format='txt', max_characters=1000)}\n\n"
                        f"{guild_info}"
                        f"**● [Channel:]({ctx.channel.jump_url})**\n"
                        f"{values.NQSP * 2}**● Name:** {ctx.channel}\n"
                        f"{values.NQSP * 2}**● ID:** `{ctx.channel.id}`\n"
                        f"**● [User:]({utilities.user_url(ctx.author.id)})**\n"
                        f"{values.NQSP * 2}**● Name:** {ctx.author}\n"
                        f"{values.NQSP * 2}**● ID:** `{ctx.author.id}`\n"
                        f"**● [Message:]({ctx.message.jump_url})**\n"
                        f"{values.NQSP * 2}**● ID:** `{ctx.message.id}`\n"
                        f"{values.NQSP * 2}**● Command:** {ctx.command.qualified_name}\n"
                        f"{values.NQSP * 2}**● Date:** {utilities.format_datetime(now, format=enums.DateTimeFormat.FULL_LONG_DATE)}\n"
                        f"{values.NQSP * 2}**● Time:** {utilities.format_datetime(now, format=enums.DateTimeFormat.FULL_TIME)}\n\n",
            thumbnail=utilities.avatar(ctx.author),
        )

    @staticmethod
    def _get_error_message(ctx: custom.Context, error: commands.CommandError) -> str | None:
        # sourcery no-metrics

        if message := ERRORS.get(type(error)):
            return message

        elif isinstance(error, commands.BadLiteralArgument):
            message = f"The **{error.param.name}** argument must exactly match one of the following:\n" \
                      f"{NL.join([f'- **{arg}**' for arg in error.literals])}"

        elif isinstance(error, commands.MissingPermissions):
            message = f"You need the following permissions to use this command:\n" \
                      f"```diff\n" \
                      f"{NL.join([f'- {permission}' for permission in error.missing_permissions])}\n" \
                      f"```"

        elif isinstance(error, commands.MissingRole):
            assert ctx.guild is not None
            message = f"You need the {ctx.guild.get_role(role) if isinstance((role := error.missing_role), int) else role} role to use this command."

        elif isinstance(error, commands.BotMissingRole):
            assert ctx.guild is not None
            message = f"I need the {ctx.guild.get_role(role) if isinstance((role := error.missing_role), int) else role} role to run this command."

        elif isinstance(error, commands.MissingAnyRole):
            assert ctx.guild is not None
            message = f"You need the following roles to use this command:\n" \
                      f"{NL.join([f'- {ctx.guild.get_role(role) if isinstance(role, int) else role}' for role in error.missing_roles])}"

        elif isinstance(error, commands.BotMissingAnyRole):
            assert ctx.guild is not None
            message = f"I need the following roles to run this command:\n" \
                      f"{NL.join([f'- {ctx.guild.get_role(role) if isinstance(role, int) else role}' for role in error.missing_roles])}"

        elif isinstance(error, commands.CommandOnCooldown):
            message = f"This command is on cooldown **{COOLDOWN_BUCKETS.get(error.type)}**. " \
                      f"You can retry in **{utilities.format_seconds(error.retry_after, friendly=True)}**"

        elif isinstance(error, commands.MaxConcurrencyReached):
            message = f"This command is already being ran at a maximum of **{error.number}** {utilities.pluralize('time', error.number)} " \
                      f"**{CONCURRENCY_BUCKETS.get(error.per)}**."

        return message

    # Utility events

    @commands.Cog.listener("on_socket_event_type")
    async def _increment_socket_event_counter(self, event_type: str) -> None:
        self.bot.socket_stats[event_type] += 1

    @commands.Cog.listener("on_message_edit")
    async def _handle_command_invoke_on_message_edit(self, before: discord.Message, after: discord.Message) -> None:

        if before.content == after.content:
            return

        await self.bot.process_commands(after)

    # Logging

    @commands.Cog.listener("on_message")
    async def _log_dm(self, message: discord.Message) -> None:

        if config.ENV is enums.Environment.DEVELOPMENT or message.guild or message.is_system() or not message.content:
            return

        content = await utilities.upload_text(self.bot.mystbin, content=message.content, format="txt")

        await self.bot.log(
            enums.LogType.DM,
            embed=utilities.embed(
                colour=values.GREEN,
                title=f"**{message.author}**",
                description=f"{content}\n\n"
                            f"**Author:** {message.author} (`{message.author.id}`)\n"
                            f"**Created:** {utilities.format_datetime(message.created_at, format=enums.DateTimeFormat.PARTIAL_LONG_DATETIME)}\n"
                            f"**Jump:** [Click here]({message.jump_url})",
                thumbnail=utilities.avatar(message.author),
                footer=f"ID: {message.id}",
            )
        )

    @commands.Cog.listener("on_guild_join")
    async def _log_guild_join(self, guild: discord.Guild) -> None:

        total = len(guild.members)
        bots = sum(1 for member in guild.members if member.bot)
        bots_percent = round((bots / total) * 100, 2)

        __log__.info(
            f"Joined a guild. {guild.name} ({guild.id}) | Members: {len(guild.members)} | Bots: {bots} ({bots_percent}%)"
        )
        await self.bot.log(
            enums.LogType.GUILD,
            embed=utilities.embed(
                colour=values.GREEN,
                title=f"Joined: **{guild}**",
                description=f"**Owner:** {guild.owner} (`{guild.owner_id}`)\n"
                            f"**Created:** {utilities.format_datetime(guild.created_at, format=enums.DateTimeFormat.PARTIAL_LONG_DATETIME)}\n"
                            f"**Joined:** {utilities.format_datetime(guild.me.joined_at, format=enums.DateTimeFormat.PARTIAL_LONG_DATETIME) if guild.me.joined_at else None}\n"
                            f"**Members:** {total}\n"
                            f"**Bots:** {bots} `{bots_percent}%`\n",
                thumbnail=utilities.icon(guild),
                footer=f"ID: {guild.id}",
            )
        )

    @commands.Cog.listener("on_guild_remove")
    async def _log_guild_remove(self, guild: discord.Guild) -> None:

        total = len(guild.members)
        bots = sum(1 for member in guild.members if member.bot)
        bots_percent = round((bots / total) * 100, 2)

        __log__.info(
            f"Left a guild. {guild.name} ({guild.id}) | Members: {len(guild.members)} | Bots: {bots} ({bots_percent}%)"
        )
        await self.bot.log(
            enums.LogType.GUILD,
            embed=utilities.embed(
                colour=values.RED,
                title=f"Left: **{guild}**",
                description=f"**Owner:** {guild.owner} (`{guild.owner_id}`)\n"
                            f"**Created:** {utilities.format_datetime(guild.created_at, format=enums.DateTimeFormat.PARTIAL_LONG_DATETIME)}\n"
                            f"**Joined:** {utilities.format_datetime(guild.me.joined_at, format=enums.DateTimeFormat.PARTIAL_LONG_DATETIME) if guild.me.joined_at else None}\n"
                            f"**Members:** {total}\n"
                            f"**Bots:** {bots} `{bots_percent}%`\n",
                thumbnail=utilities.icon(guild),
                footer=f"ID: {guild.id}",
            )
        )

    @commands.Cog.listener("on_command_completion")
    async def _log_command_use(self, ctx: custom.Context) -> None:

        await self.bot.logging_webhooks[enums.LogType.COMMAND].send(
            embed=await self._build_command_information_embed(ctx, colour=values.GREEN),
            username=f"{ctx.guild or ctx.author}",
            avatar_url=utilities.icon(ctx.guild) if ctx.guild else utilities.avatar(ctx.author),
        )

    @commands.Cog.listener("on_command_error")
    async def _log_command_error(self, ctx: custom.Context, error: commands.CommandError) -> None:

        error = getattr(error, "original", error)

        if isinstance(error, exceptions.EmbedError):
            await ctx.reply(embed=error.embed)

        elif isinstance(error, commands.CommandNotFound):
            await ctx.message.add_reaction(values.STOP)
            if self.bot.user:
                await asyncio.sleep(3)
                await ctx.message.remove_reaction(values.STOP, self.bot.user)

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.try_dm(
                embed=utilities.embed(
                    colour=values.RED,
                    description=f"I need the following permissions to run that command:\n"
                                f"{utilities.codeblock(NL.join([f'- {permission}' for permission in error.missing_permissions]), language='diff')}"
                )
            )

        elif message := self._get_error_message(ctx, error):
            await ctx.reply(
                embed=utilities.embed(
                    colour=values.RED,
                    description=message.format(error=error),
                    footer=f"Use '{ctx.prefix}help {ctx.command.qualified_name if ctx.command else 'Unknown'}' for more info.",
                )
            )

        else:

            # Format exception and log to console.

            exception = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            __log__.error(
                f"Error running command '{ctx.command.qualified_name if ctx.command else 'Unknown'}':\n{exception}"
            )

            # Send friendly error message to user.

            view = discord.ui.View().add_item(
                discord.ui.Button(label="Support Server", url=values.SUPPORT_LINK)
            )

            await ctx.reply(
                embed=utilities.embed(
                    colour=values.RED,
                    description="Something went wrong!",
                ),
                view=view
            )

            # Log error to webhook.

            webhook_username = f"{ctx.guild or ctx.author}"
            webhook_avatar = utilities.icon(ctx.guild) if ctx.guild else utilities.avatar(ctx.author)

            await self.bot.logging_webhooks[enums.LogType.ERROR].send(
                await utilities.upload_text(
                    self.bot.mystbin,
                    content=utilities.codeblock(exception, max_characters=2000),
                    format="python",
                    max_characters=2000
                ),
                embed=await self._build_command_information_embed(ctx, colour=values.RED),
                username=webhook_username,
                avatar_url=webhook_avatar,
            )

    # Voice events

    @commands.Cog.listener("on_voice_state_update")
    async def _handle_player_disconnect(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ) -> None:

        assert self.bot.user is not None

        if member.id != self.bot.user.id:
            return

        if (
                before.channel is not None and
                after.channel is None and
                before.channel.guild.voice_client is not None
        ):
            await before.channel.guild.voice_client.disconnect(force=True)

    @commands.Cog.listener("on_slate_track_start")
    async def _handle_track_start(self, player: custom.Player, _: slate.TrackStart) -> None:
        await player.handle_track_start()

    @commands.Cog.listener("on_slate_track_end")
    async def _handle_track_end(self, player: custom.Player, event: slate.TrackEnd) -> None:

        if event.reason == "REPLACED":
            return

        await player.handle_track_end(enums.TrackEndReason.NORMAL)

    @commands.Cog.listener("on_slate_track_stuck")
    async def _handle_track_stuck(self, player: custom.Player, _: slate.TrackStuck) -> None:
        await player.handle_track_end(enums.TrackEndReason.STUCK)

    @commands.Cog.listener("on_slate_track_exception")
    async def _handle_track_exception(self, player: custom.Player, _: slate.TrackException) -> None:
        await player.handle_track_end(enums.TrackEndReason.EXCEPTION)
