# Standard Library
import asyncio
import dataclasses
from collections.abc import Callable
from typing import TypeVar

# Libraries
import discord
from discord.ext import commands
from typing_extensions import Self

# Project
from cd import custom, utilities, values
from cd.config import CONFIG
from cd.enums import Environment


__all__ = [
    "original",
    "command_not_found",
    "HANDLERS",
]


@dataclasses.dataclass
class Response:
    description: str
    footer: str | None = None


async def original(
    error: Exception,
    ctx: custom.Context
) -> None:
    embed = utilities.embed(
        colour=values.ERROR_COLOUR,
        description=f"Something went wrong!"
    )
    if CONFIG.general.environment == Environment.DEVELOPMENT:
        await ctx.reply(
            embed=embed,
            content=utilities.codeblock(utilities.format_traceback(error), "py")
        )
    else:
        await ctx.reply(
            embed=embed,
            view=discord.ui.View().add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="Support Server",
                    url=values.SUPPORT_SERVER_URL
                )
            )
        )


async def command_not_found(
    error: commands.CommandNotFound,
    ctx: custom.Context
) -> None:
    await ctx.message.add_reaction(values.STOP_EMOJI)
    await asyncio.sleep(2.5)
    await ctx.message.remove_reaction(values.STOP_EMOJI, ctx.me)


def disabled_command(
    error: commands.DisabledCommand,
    ctx: custom.Context
) -> Response:
    return Response(description="This command is disabled.")


def command_on_cooldown(
    error: commands.CommandOnCooldown,
    ctx: custom.Context
) -> Response:
    buckets = {
        commands.BucketType.default:  f" **across the whole bot**",
        commands.BucketType.user:     f" **for you** in **all servers**",
        commands.BucketType.member:   f" **for you** in **this server**",
        commands.BucketType.guild:    f" in **this server**",
        commands.BucketType.channel:  f" in **this channel**",
        commands.BucketType.category: f" in **this channel category**",
        commands.BucketType.role:     f" for **users** with the **same top role as you**",
    }
    return Response(
        description=f"This command is on cooldown{buckets.get(error.type, '')}.",
        footer=f"You can retry in {utilities.format_seconds(error.retry_after)}.",
    )


def max_concurrency_reached(
    error: commands.MaxConcurrencyReached,
    ctx: custom.Context
) -> Response:
    buckets = {
        commands.BucketType.default:  f"**across the whole bot**",
        commands.BucketType.user:     f"**by you** in **all servers**",
        commands.BucketType.member:   f"**by you** in **this server**",
        commands.BucketType.guild:    f"in **this server**",
        commands.BucketType.channel:  f"in **this channel**",
        commands.BucketType.category: f"in **this channel category**",
        commands.BucketType.role:     f"by **users** with the **same top role as you**",
    }
    return Response(
        description=f"This command is being used too many times at once {buckets[error.per]}.",
        footer=f"It can be used {error.number} {utilities.plural('time', error.number)} at once "
               f"{discord.utils.remove_markdown(buckets[error.per])}",
    )


def missing_required_argument(
    error: commands.MissingRequiredArgument,
    ctx: custom.Context
) -> Response:
    return Response(description=f"You didn't provide the **{error.param.name}** argument.")


def missing_required_attachment(
    error: commands.MissingRequiredArgument,
    ctx: custom.Context
) -> Response:
    return Response(description=f"You didn't provide an attachment for the **{error.param.name}** argument.")


def too_many_arguments(
    error: commands.TooManyArguments,
    ctx: custom.Context
) -> Response:
    return Response(description="You provided too many arguments.")


def bad_union_argument(
    error: commands.BadUnionArgument,
    ctx: custom.Context
) -> Response:
    return Response(description=f"Your input for the **{error.param.name}** argument is not valid.")


def bad_literal_argument(
    error: commands.BadLiteralArgument,
    ctx: custom.Context
) -> Response:
    return Response(
        description=f"Your input for the **{error.param.name}** argument must match one of the following:\n"
                    f"{values.NL.join(f'- {value}' for value in error.literals)}"
    )


def bad_argument(
    error: commands.BadArgument,
    ctx: custom.Context
) -> Response:
    return Response(description=f"Your input for one of this command's arguments is not valid.")


type NotFoundError = (
    commands.MessageNotFound | commands.MemberNotFound | commands.GuildNotFound | commands.UserNotFound |
    commands.ChannelNotFound | commands.RoleNotFound | commands.EmojiNotFound | commands.GuildStickerNotFound |
    commands.ScheduledEventNotFound | commands.ThreadNotFound | commands.BadColourArgument |
    commands.PartialEmojiConversionFailure
)


def not_found(thing: str) -> Callable[[NotFoundError, custom.Context], Response]:
    def handler(
        error: NotFoundError,
        ctx: custom.Context
    ) -> Response:
        return Response(
            description=f"I couldn't find {thing} that matches **{utilities.truncate(str(error.argument), 25)}**."
        )

    return handler


def channel_not_readable(
    error: commands.ChannelNotReadable,
    ctx: custom.Context
) -> Response:
    return Response(description=f"I don't have permission to read messages in {error.argument.mention}.")


def bad_invite_argument(
    error: commands.BadInviteArgument,
    ctx: custom.Context
) -> Response:
    return Response(
        description=f"Your input of **{utilities.truncate(error.argument, 25)}** isn't a valid invite."
    )


def bad_bool_argument(
    error: commands.BadBoolArgument,
    ctx: custom.Context
) -> Response:
    return Response(
        description=f"Your input of **{utilities.truncate(error.argument, 25)}** isn't a valid boolean value.",
        footer="Valid boolean values are; yes, no, true, false, on, off, enable, disable, 1, and 0."
    )


def bad_range_argument(
    error: commands.RangeError,
    ctx: custom.Context
) -> Response:
    if error.minimum and error.maximum:
        message = f"between **{error.minimum}** and **{error.maximum}**"
    elif error.minimum:
        message = f"more than **{error.minimum}**"
    elif error.maximum:
        message = f"less than **{error.maximum}**"
    else:
        message = "a **valid number**"
    return Response(description=f"Your input of **{utilities.truncate(str(error.value), 10)}** should be {message}.")


def bad_flag_argument(
    error: commands.BadFlagArgument,
    ctx: custom.Context
) -> Response:
    return Response(
        description=f"Your input of **{utilities.truncate(error.argument, 25)}** for the **{error.flag.name}** flag "
                    f"could not be converted."
    )


def missing_flag_argument(
    error: commands.MissingFlagArgument,
    ctx: custom.Context
) -> Response:
    return Response(
        description=f"You didn't provide a value for the **{error.flag.name}** flag."
    )


def too_many_flags(
    error: commands.TooManyFlags,
    ctx: custom.Context
) -> Response:
    return Response(
        description=f"You provided too many values for the **{error.flag.name}** flag."
    )


def missing_required_flag(
    error: commands.MissingRequiredFlag,
    ctx: custom.Context
) -> Response:
    return Response(
        description=f"You didn't provide the **{error.flag.name}** flag."
    )


def unexpected_quote(
    error: commands.UnexpectedQuoteError,
    ctx: custom.Context
) -> Response:
    return Response(
        description=f"An unexpected quote mark (**{error.quote}**) was found in your input.",
        footer="You can escape intentional quote marks with a backslash (\\)."
    )


def invalid_end_of_quoted_string(
    error: commands.InvalidEndOfQuotedStringError,
    ctx: custom.Context
) -> Response:
    return Response(
        description=f"A closing quote mark followed by an unexpected character (**{error.char}**) was found in your input.",
        footer="Closing quote marks can only be followed by a space or nothing at all."
    )


def expected_closing_quote(
    error: commands.ExpectedClosingQuoteError,
    ctx: custom.Context
) -> Response:
    return Response(
        description=f"You missed a closing quote mark (**{error.close_quote}**) in your input.",
        footer="You can escape intentional quote marks with a backslash (\\)."
    )


def check_failure(
    error: commands.CheckFailure,
    ctx: custom.Context
) -> Response:
    return Response(description="You don't meet the requirements to use this command.")


def check_any_failure(
    error: commands.CheckAnyFailure,
    ctx: custom.Context
) -> Response:
    return Response(description="You don't meet the requirements to use this command.")


def private_message_only(
    error: commands.PrivateMessageOnly,
    ctx: custom.Context
) -> Response:
    return Response(description="This command can only be used in DM's.")


def no_private_message(
    error: commands.NoPrivateMessage,
    ctx: custom.Context
) -> Response:
    return Response(description="This command can not be used in DM's.")


def not_owner(
    error: commands.NotOwner,
    ctx: custom.Context
) -> Response:
    return Response(description="This command can only be used by the bots owners.")


def missing_permissions(
    error: commands.MissingPermissions | commands.BotMissingPermissions,
    ctx: custom.Context
) -> Response:
    permissions = "".join(
        [
            f"- {permission.replace('_', ' ').replace('guild', 'server').title()}"
            for permission in error.missing_permissions
        ]
    )
    descriptions = {
        commands.MissingPermissions:    f"You need the following permissions to use this command:\n{permissions}",
        commands.BotMissingPermissions: f"I need the following permissions to run this command:\n{permissions}"
    }
    return Response(description=descriptions[type(error)])


def missing_role(
    error: commands.MissingRole | commands.BotMissingRole,
    ctx: custom.Context
) -> Response:
    role = utilities.role_mention(ctx, error.missing_role)
    descriptions = {
        commands.MissingRole:    f"You need the {role} role to use this command.",
        commands.BotMissingRole: f"I need the {role} role to use this command."
    }
    return Response(description=descriptions[type(error)])


def missing_any_role(
    error: commands.MissingAnyRole | commands.BotMissingAnyRole,
    ctx: custom.Context
) -> Response:
    roles = [utilities.role_mention(ctx, role) for role in error.missing_roles]
    descriptions = {
        commands.MissingAnyRole:    f"You need one of the following roles to use this command:\n{values.NL.join(roles)}",
        commands.BotMissingAnyRole: f"I need one of the following roles to use this command:\n{values.NL.join(roles)}",
    }
    return Response(description=descriptions[type(error)])


def nsfw_channel_required(
    error: commands.NSFWChannelRequired,
    ctx: custom.Context
) -> Response:
    return Response(description="This command can only be used in NSFW channels.")


T = TypeVar("T", bound=commands.CommandError, contravariant=True)


class Handlers:

    def __getitem__(self: Self, item: type[T]) -> Callable[[T, custom.Context], Response]:
        ...

    def __contains__(self: Self, item: type[T]) -> bool:
        ...


HANDLERS: Handlers = {  # type: ignore
    # commands.CommandError ->
    commands.DisabledCommand:               disabled_command,
    commands.CommandOnCooldown:             command_on_cooldown,
    commands.MaxConcurrencyReached:         max_concurrency_reached,
    # commands.CommandError -> commands.UserInputError ->
    commands.MissingRequiredArgument:       missing_required_argument,
    commands.MissingRequiredAttachment:     missing_required_attachment,
    commands.TooManyArguments:              too_many_arguments,
    commands.BadUnionArgument:              bad_union_argument,
    commands.BadLiteralArgument:            bad_literal_argument,
    # commands.CommandError -> commands.UserInputError -> commands.BadArgument ->
    commands.BadArgument:                   bad_argument,
    commands.UserNotFound:                  not_found("a **user**"),
    commands.GuildNotFound:                 not_found("a **server**"),
    commands.MemberNotFound:                not_found("a **member**"),
    commands.RoleNotFound:                  not_found("a **role**"),
    commands.ChannelNotFound:               not_found("a **channel**"),
    commands.ThreadNotFound:                not_found("a **thread**"),
    commands.MessageNotFound:               not_found("a **message**"),
    commands.GuildStickerNotFound:          not_found("a **sticker**"),
    commands.BadColourArgument:             not_found("a **colour**"),
    commands.EmojiNotFound:                 not_found("an **emoji**"),
    commands.PartialEmojiConversionFailure: not_found("an **emoji**"),
    commands.ScheduledEventNotFound:        not_found("an **event**"),
    commands.ChannelNotReadable:            channel_not_readable,
    commands.BadInviteArgument:             bad_invite_argument,
    commands.BadBoolArgument:               bad_bool_argument,
    commands.RangeError:                    bad_range_argument,
    # commands.CommandError -> commands.UserInputError -> commands.BadArgument -> commands.FlagError ->
    commands.BadFlagArgument:               bad_flag_argument,
    commands.MissingFlagArgument:           missing_flag_argument,
    commands.TooManyFlags:                  too_many_flags,
    commands.MissingRequiredFlag:           missing_required_flag,
    # commands.CommandError -> commands.UserInputError -> commands.ArgumentParsingError ->
    commands.UnexpectedQuoteError:          unexpected_quote,
    commands.InvalidEndOfQuotedStringError: invalid_end_of_quoted_string,
    commands.ExpectedClosingQuoteError:     expected_closing_quote,
    # commands.CommandError -> commands.CheckFailure ->
    commands.CheckFailure:                  check_failure,
    commands.CheckAnyFailure:               check_any_failure,
    commands.PrivateMessageOnly:            private_message_only,
    commands.NoPrivateMessage:              no_private_message,
    commands.NotOwner:                      not_owner,
    commands.MissingPermissions:            missing_permissions,
    commands.BotMissingPermissions:         missing_permissions,
    commands.MissingRole:                   missing_role,
    commands.BotMissingRole:                missing_role,
    commands.MissingAnyRole:                missing_any_role,
    commands.BotMissingAnyRole:             missing_any_role,
    commands.NSFWChannelRequired:           nsfw_channel_required,
}
