# Future
from __future__ import annotations

# Standard Library
import abc
import inspect
from collections import defaultdict
from typing import Any, Awaitable, Callable, Concatenate, Literal, ParamSpec, Type, TypeVar, Union, get_args, get_origin

# Packages
import discord
import discord.ext.commands._types
import discord.state
import discord.types.interactions
from discord.ext import commands

# My stuff
from utilities import utils
from utilities.slash.cog import ApplicationCog
from utilities.slash.context import ApplicationContext
from utilities.slash.types import Range


__all__ = (
    "ApplicationCommand",
    "SlashCommand",
    "slash_command",
    "describe"
)


CogT = TypeVar("CogT", bound=ApplicationCog)
ContextT = TypeVar("ContextT", bound=ApplicationContext)

CommandParams = ParamSpec("CommandParams")
CommandT = Callable[Concatenate[CogT, ContextT, CommandParams], Awaitable[Any]]


APPLICATION_COMMAND_OPTION_TYPE_MAP: dict[Type[Any], int] = {
    # "subcommand":          1,
    # "subcommand_group":    2,
    str:                     3,
    int:                     4,
    bool:                    5,
    discord.User:            6,
    discord.Member:          6,
    discord.TextChannel:     7,
    discord.VoiceChannel:    7,
    discord.CategoryChannel: 7,
    discord.Role:            8,
    # Mentionable:           9,
    float:                   10
}
CHANNEL_TYPE_FILTER: dict[Type[discord.abc.GuildChannel], int] = {
    discord.TextChannel:     0,
    discord.VoiceChannel:    2,
    discord.CategoryChannel: 4
}


def _parse_resolved_data(interaction: discord.Interaction, state: discord.state.ConnectionState) -> dict[int, Any]:

    if not (data := interaction.data.get("resolved")):  # type: ignore
        return {}

    assert interaction.guild

    resolved = {}

    if resolved_users := data.get("users"):
        resolved_members = data["members"]  # type: ignore

        for id, user_data in resolved_users.items():
            member_data = resolved_members[id]
            member_data["user"] = user_data  # type: ignore

            resolved[int(id)] = discord.Member(data=member_data, guild=interaction.guild, state=state)  # type: ignore

    if resolved_channels := data.get("channels"):

        for id, channel_data in resolved_channels.items():
            channel_data["position"] = None  # type: ignore
            cls, _ = discord.channel._guild_channel_factory(channel_data["type"])

            resolved[int(id)] = cls(state=state, guild=interaction.guild, data=channel_data)

    if resolved_messages := data.get("messages"):
        for id, message_data in resolved_messages.items():
            resolved[int(id)] = discord.Message(state=state, channel=interaction.channel, data=message_data)  # type: ignore

    if resolved_roles := data.get("roles"):
        for id, role_data in resolved_roles.items():
            resolved[int(id)] = discord.Role(guild=interaction.guild, state=state, data=role_data)

    return resolved


class ApplicationCommand(abc.ABC):

    function: Callable
    cog: ApplicationCog
    name: str
    guild_id: int | None
    checks: list[discord.ext.commands._types.Check]

    qualified_name: str

    #

    @abc.abstractmethod
    def _build_payload(self) -> dict[str, Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def _build_arguments(self, interaction: discord.Interaction, state: discord.state.ConnectionState) -> dict[str, Any]:
        raise NotImplementedError

    #

    async def invoke(self, context: ApplicationContext, **params) -> None:

        if not await self.can_run(context):
            raise commands.CheckFailure(f"The check functions for application command '{self.name}' failed.")

        await self.function(self.cog, context, **params)

    async def can_run(self, ctx: ApplicationContext) -> bool:

        if not await ctx.bot.can_run(ctx):  # type: ignore
            raise commands.CheckFailure(f"The global check functions for application command '{self.name}' failed.")

        if ((cog := self.cog) is not None and (
                (cog_check := ApplicationCog._get_overridden_method(cog.cog_check)) is not None
                and await discord.utils.maybe_coroutine(cog_check, ctx) is False
        )):
            return False

        if not (predicates := self.checks):
            return True

        return await discord.utils.async_all(predicate(ctx) for predicate in predicates)  # type: ignore


class SlashCommand(ApplicationCommand):

    def __init__(self, function: CommandT, **kwargs) -> None:

        self.function: CommandT = function
        self.cog: ApplicationCog = utils.MISSING
        self.name: str = kwargs.get("name", function.__name__)
        self.guild_id: int | None = kwargs.get("guild_id")
        try:
            checks = function.__commands_checks__  # type: ignore
        except AttributeError:
            checks = kwargs.get("checks", [])
        self.checks: list[commands._types.Check] = checks  # type: ignore

        self.parameters: dict[str, inspect.Parameter] = self._build_parameters()

        self.description: str = kwargs.get("description") or function.__doc__ or "No description provided"
        self.parameter_descriptions: dict[str, str] = defaultdict(lambda: "No description provided")

        # Compatability with discord.py
        self.qualified_name: str = self.name

    #

    def _build_payload(self) -> dict[str, Any]:
        # sourcery no-metrics

        self._build_descriptions()

        payload: dict[str, Any] = {
            "name":        self.name,
            "description": self.description,
            "type":        1
        }

        if params := self.parameters:

            options = []

            for name, parameter in params.items():

                annotation = parameter.annotation

                if annotation is parameter.empty:
                    raise TypeError(f"missing type annotation for parameter '{parameter.name}' for command '{self.name}'.")

                if isinstance(annotation, str):
                    annotation = eval(annotation)

                if isinstance(annotation, Range):
                    real_type = type(annotation.max)
                elif get_origin(annotation) is Union:
                    args = get_args(annotation)
                    real_type = args[0]
                elif get_origin(annotation) is Literal:
                    real_type = type(annotation.__args__[0])
                else:
                    real_type = annotation

                option: dict[str, Any] = {
                    "type":        APPLICATION_COMMAND_OPTION_TYPE_MAP[real_type],
                    "name":        name,
                    "description": self.parameter_descriptions[name]
                }
                if parameter.default is parameter.empty:
                    option["required"] = True

                if isinstance(annotation, Range):
                    option["max_value"] = annotation.max
                    option["min_value"] = annotation.min

                elif get_origin(annotation) is Union:

                    arguments = get_args(annotation)

                    if not all(issubclass(argument_type, discord.abc.GuildChannel) for argument_type in arguments):
                        raise TypeError("Union parameter types only supported on GuildChannel types")

                    if len(arguments) != 3:
                        filtered = [CHANNEL_TYPE_FILTER[i] for i in arguments]
                        option["channel_types"] = filtered

                elif get_origin(annotation) is Literal:
                    arguments = annotation.__args__
                    option["choices"] = [{"name": str(a), "value": a} for a in arguments]

                elif issubclass(annotation, discord.abc.GuildChannel):
                    option["channel_types"] = [CHANNEL_TYPE_FILTER[annotation]]

                options.append(option)

            options.sort(key=lambda f: not f.get("required"))
            payload["options"] = options

        return payload

    def _build_arguments(self, interaction: discord.Interaction, state: discord.state.ConnectionState) -> dict[str, Any]:

        if "options" not in interaction.data:  # type: ignore
            return {}

        resolved = _parse_resolved_data(interaction, state)
        result = {}

        for option in interaction.data["options"]:  # type: ignore
            value = option["value"]  # type: ignore

            if option["type"] in (6, 7, 8):
                value = resolved[int(value)]

            result[option["name"]] = value

        return result

    #

    def _build_parameters(self) -> dict[str, inspect.Parameter]:

        params = list(inspect.signature(self.function).parameters.values())
        try:
            params.pop(0)
        except IndexError:
            raise ValueError("expected argument 'self' is missing")

        try:
            params.pop(0)
        except IndexError:
            raise ValueError("expected argument 'context' is missing")

        return {p.name: p for p in params}

    def _build_descriptions(self) -> None:

        if not hasattr(self.function, "_param_desc_"):
            return

        for name, description in self.function._param_desc_.items():  # type: ignore
            if name not in self.parameters:
                raise TypeError(f"@describe used to describe a non-existent parameter '{name}'.")

            self.parameter_descriptions[name] = description


def slash_command(**kwargs) -> Callable[[CommandT], SlashCommand]:

    def _inner(function: CommandT) -> SlashCommand:
        return SlashCommand(function, **kwargs)

    return _inner


def describe(**kwargs) -> Any:

    def _inner(command: SlashCommand) -> Any:

        function = command.function if isinstance(command, SlashCommand) else command

        for name, description in kwargs.items():
            try:
                function._param_desc_[name] = description
            except AttributeError:
                function._param_desc_ = {name: description}

        return command

    return _inner
