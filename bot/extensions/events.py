# Future
from __future__ import annotations

# Standard Library
import asyncio
import logging
import traceback
from typing import Type

# Packages
import discord
import pendulum
import slate.obsidian
from discord.ext import commands

# My stuff
from core import config, values
from core.bot import CD
from utilities import custom, enums, exceptions, utils


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

ERRORS: dict[Type[commands.CommandError], str] = {
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


def setup(bot: CD) -> None:
    bot.add_cog(Events(bot))


class Events(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

    # Bot events

    @commands.Cog.listener()
    async def on_socket_event_type(self, event_type: str) -> None:
        self.bot.socket_stats[event_type] += 1

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:

        if before.content == after.content:
            return

        await self.bot.process_commands(after)

    # Guild logging

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:

        total = len(guild.members)
        bots = sum(1 for member in guild.members if member.bot)
        bots_percent = round((bots / total) * 100, 2)

        __log__.info(f"Joined a guild. {guild.name} ({guild.id}) | Members: {len(guild.members)} | Bots: {bots} ({bots_percent}%)")
        await self.bot.log(
            enums.LogType.GUILD,
            embed=utils.embed(
                colour=values.GREEN,
                title=f"Joined: **{guild}**",
                description=f"**Owner:** {guild.owner} (`{guild.owner_id}`)\n"
                            f"**Created:** {utils.format_datetime(guild.created_at, format=enums.DatetimeFormat.PARTIAL_LONG_DATETIME)}\n"
                            f"**Joined:** {utils.format_datetime(guild.me.joined_at, format=enums.DatetimeFormat.PARTIAL_LONG_DATETIME) if guild.me.joined_at else None}\n"
                            f"**Members:** {total}\n"
                            f"**Bots:** {bots} `{bots_percent}%`\n",
                thumbnail=utils.icon(guild),
                footer=f"ID: {guild.id}",
            )
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:

        total = len(guild.members)
        bots = sum(1 for member in guild.members if member.bot)
        bots_percent = round((bots / total) * 100, 2)

        __log__.info(f"Left a guild. {guild.name} ({guild.id}) | Members: {len(guild.members)} | Bots: {bots} ({bots_percent}%)")
        await self.bot.log(
            enums.LogType.GUILD,
            embed=utils.embed(
                colour=values.RED,
                title=f"Left: **{guild}**",
                description=f"**Owner:** {guild.owner} (`{guild.owner_id}`)\n"
                            f"**Created:** {utils.format_datetime(guild.created_at, format=enums.DatetimeFormat.PARTIAL_LONG_DATETIME)}\n"
                            f"**Joined:** {utils.format_datetime(guild.me.joined_at, format=enums.DatetimeFormat.PARTIAL_LONG_DATETIME) if guild.me.joined_at else None}\n"
                            f"**Members:** {total}\n"
                            f"**Bots:** {bots} `{bots_percent}%`\n",
                thumbnail=utils.icon(guild),
                footer=f"ID: {guild.id}",
            )
        )

    # DM logging

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        if config.ENV is enums.Environment.DEVELOPMENT or message.guild or message.is_system() or not message.content:
            return

        content = await utils.upload_text(self.bot.mystbin, content=message.content, format="txt")

        await self.bot.log(
            enums.LogType.DM,
            embed=utils.embed(
                colour=values.GREEN,
                title=f"**{message.author}**",
                description=f"{content}\n\n"
                            f"**Author:** {message.author} (`{message.author.id}`)\n"
                            f"**Created:** {utils.format_datetime(message.created_at, format=enums.DatetimeFormat.PARTIAL_LONG_DATETIME)}\n"
                            f"**Jump:** [Click here]({message.jump_url})",
                thumbnail=utils.avatar(message.author),
                footer=f"ID: {message.id}",
            )
        )

    # Error logging

    @staticmethod
    def _get_error_message(ctx: custom.Context, error: commands.CommandError) -> str | None:

        # sourcery no-metrics

        if message := ERRORS.get(type(error)):
            return message

        elif isinstance(error, commands.ConversionError):
            message = "TODO"

        elif isinstance(error, commands.BadLiteralArgument):
            message = f"The **{error.param.name}** argument must exactly match one of the following:\n" \
                      f"{values.NL.join([f'- **{arg}**' for arg in error.literals])}"

        elif isinstance(error, commands.MissingPermissions):
            message = f"You need the following permissions to use this command:\n" \
                      f"```diff\n" \
                      f"{values.NL.join([f'- {permission}' for permission in error.missing_permissions])}\n" \
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
                      f"{values.NL.join([f'- {ctx.guild.get_role(role) if isinstance(role, int) else role}' for role in error.missing_roles])}"

        elif isinstance(error, commands.BotMissingAnyRole):
            assert ctx.guild is not None
            message = f"I need the following roles to run this command:\n" \
                      f"{values.NL.join([f'- {ctx.guild.get_role(role) if isinstance(role, int) else role}' for role in error.missing_roles])}"

        elif isinstance(error, commands.CommandOnCooldown):
            message = f"This command is on cooldown **{COOLDOWN_BUCKETS.get(error.type)}**. " \
                      f"You can retry in **{utils.format_seconds(error.retry_after, friendly=True)}**"

        elif isinstance(error, commands.MaxConcurrencyReached):
            message = f"This command is already being ran at a maximum of **{error.number}** time{'s' if error.number > 1 else ''} " \
                      f"**{CONCURRENCY_BUCKETS.get(error.per)}**."

        return message

    @staticmethod
    async def _send_friendly_error(ctx: custom.Context) -> None:

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Support server", url=values.SUPPORT_LINK))

        await ctx.reply(
            embed=utils.embed(
                colour=values.RED,
                description="Something went wrong!",
            ),
            view=view
        )

    async def _send_exception(self, ctx: custom.Context, exception: str) -> None:

        guild_url = f"https://canary.discord.com/channels/{ctx.guild.id}" if ctx.guild else None
        channel_url = f"https://canary.discord.com/channels/{ctx.guild.id if ctx.guild else '@me'}/{ctx.channel.id}"
        user_url = f"https://canary.discord.com/users/{ctx.author.id}"

        guild_info = f"**● [Guild:]({guild_url})**\n" \
                     f"{values.NQSP * 2}**● Name:** {ctx.guild}\n" \
                     f"{values.NQSP * 2}**● ID:** `{ctx.guild.id}`\n" \
            if ctx.guild else ""

        webhook_avatar = utils.icon(ctx.guild) if ctx.guild else utils.avatar(ctx.author)
        webhook_username = f"{ctx.guild or ctx.author}"

        await self.bot.log_webhooks[enums.LogType.ERROR].send(
            embed=utils.embed(
                colour=values.RED,
                description=f"{await utils.upload_text(self.bot.mystbin, content=ctx.message.content, format='python', max_characters=1000)}\n\n"
                            f"{guild_info}"
                            f"**● [Channel:]({channel_url})**\n"
                            f"{values.NQSP * 2}**● Name:** {ctx.channel}\n"
                            f"{values.NQSP * 2}**● ID:** `{ctx.channel.id}`\n"
                            f"**● [User:]({user_url})**\n"
                            f"{values.NQSP * 2}**● Name:** {ctx.author}\n"
                            f"{values.NQSP * 2}**● ID:** `{ctx.author.id}`\n"
                            f"**● [Message:]({ctx.message.jump_url})**\n"
                            f"{values.NQSP * 2}**● ID:** `{ctx.message.id}`\n"
                            f"{values.NQSP * 2}**● Command:** {ctx.command.qualified_name if ctx.command else 'Unknown'}\n"
                            f"{values.NQSP * 2}**● When:** {utils.format_datetime(pendulum.now(tz='UTC'), format=enums.DatetimeFormat.PARTIAL_LONG_DATETIME)}\n\n",
                thumbnail=utils.avatar(ctx.author),
            ),
            username=webhook_username,
            avatar_url=webhook_avatar,
        )

        await self.bot.log_webhooks[enums.LogType.ERROR].send(
            content=await utils.upload_text(
                self.bot.mystbin,
                content=f"```py\n{exception}\n```" if len(exception) < 2000 else exception,
                format="python",
                max_characters=2000
            ),
            username=webhook_username,
            avatar_url=webhook_avatar,
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: custom.Context, error: commands.CommandError) -> None:

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            await ctx.message.add_reaction(values.STOP)
            if self.bot.user:
                await asyncio.sleep(3)
                await ctx.message.remove_reaction(values.STOP, self.bot.user)

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.try_dm(
                embed=utils.embed(
                    colour=values.RED,
                    description=f"I need the following permissions to run this command:\n"
                                f"```diff\n"
                                f"{values.NL.join([f'- {permission}' for permission in error.missing_permissions])}\n"
                                f"```"
                )
            )

        elif isinstance(error, exceptions.EmbedError):
            await ctx.reply(embed=error.embed)

        elif message := self._get_error_message(ctx, error):
            await ctx.reply(
                embed=utils.embed(
                    colour=values.RED,
                    description=message.format(error=error),
                    footer=f"Use '{ctx.prefix}help {ctx.command.qualified_name}' for more info." if ctx.command else None,
                )
            )

        else:

            exception = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            __log__.error(f"Error running command '{ctx.command.qualified_name if ctx.command else 'Unknown'}':\n{exception}")

            await self._send_friendly_error(ctx)
            await self._send_exception(ctx, exception)

    # Command logging

    @commands.Cog.listener()
    async def on_command(self, ctx: custom.Context) -> None:

        assert ctx.command is not None

        await self.bot.log_webhooks[enums.LogType.COMMAND].send(
            embed=utils.embed(
                colour=values.GREEN,
                title=f"{ctx.prefix}{ctx.command.qualified_name}",
                description=f"{await utils.upload_text(self.bot.mystbin, content=ctx.message.content, format='python', max_characters=2000)}\n\n"
                            f"{f'**Guild:** {ctx.guild} (`{ctx.guild.id}`){values.NL}' if ctx.guild else ''}"
                            f"**Channel:** {ctx.channel} (`{ctx.channel.id}`)\n"
                            f"**Author:** {ctx.author} (`{ctx.author.id}`)\n"
                            f"**Time:** {utils.format_datetime(pendulum.now(tz='UTC'), format=enums.DatetimeFormat.PARTIAL_LONG_DATETIME)}",
            ),
            username=f"{ctx.author}",
            avatar_url=utils.avatar(ctx.author)
        )

    @commands.Cog.listener("on_voice_state_update")
    async def voice_client_cleanup(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:

        assert self.bot.user is not None

        if member.id != self.bot.user.id:
            return

        if (
                before.channel is not None and
                after.channel is None and
                before.channel.guild.voice_client is not None
        ):
            await before.channel.guild.voice_client.disconnect(force=True)

    # Slate events

    @commands.Cog.listener()
    async def on_obsidian_track_start(self, player: custom.Player, _: slate.obsidian.TrackStart) -> None:
        await player.handle_track_start()

    @commands.Cog.listener()
    async def on_obsidian_track_end(self, player: custom.Player, _: slate.obsidian.TrackEnd) -> None:
        await player.handle_track_end()

    @commands.Cog.listener()
    async def on_obsidian_track_stuck(self, player: custom.Player, _: slate.obsidian.TrackStuck) -> None:
        await player.handle_track_end(error=True)

    @commands.Cog.listener()
    async def on_obsidian_track_exception(self, player: custom.Player, _: slate.obsidian.TrackException) -> None:
        await player.handle_track_end(error=True)
