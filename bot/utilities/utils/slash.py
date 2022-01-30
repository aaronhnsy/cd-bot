# Future
from __future__ import annotations

# Standard Library
import inspect
import traceback
from collections import defaultdict
from typing import (
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    Literal,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    overload,
)

# Packages
import discord
import discord.state
from discord.ext import commands
from discord.utils import MISSING
from typing_extensions import Concatenate, ParamSpec

# My stuff
from utilities import custom, exceptions


BotT = TypeVar("BotT", bound='Bot')
CtxT = TypeVar("CtxT", bound='Context')
CogT = TypeVar("CogT", bound='ApplicationCog')
NumT = int | float

CmdP = ParamSpec("CmdP")
CmdT = Callable[Concatenate[CogT, CtxT, CmdP], Awaitable[Any]]
MsgCmdT = Callable[[CogT, CtxT, discord.Message], Awaitable[Any]]
UsrCmdT = Callable[[CogT, CtxT, discord.Member], Awaitable[Any]]
CtxMnT = MsgCmdT | UsrCmdT

RngT = TypeVar("RngT", bound="Range")

__all__ = [
    "describe",
    "SlashCommand",
    "ApplicationCog",
    "Range",
    "Context",
    "Bot",
    "slash_command",
    "message_command",
    "user_command"
]

command_type_map: dict[Type[Any], int] = {
    str:                     3,
    int:                     4,
    bool:                    5,
    discord.User:            6,
    discord.Member:          6,
    discord.TextChannel:     7,
    discord.VoiceChannel:    7,
    discord.CategoryChannel: 7,
    discord.Role:            8,
    float:                   10
}

channel_filter: dict[Type[discord.abc.GuildChannel], int] = {
    discord.TextChannel:     0,
    discord.VoiceChannel:    2,
    discord.CategoryChannel: 4
}


def describe(**kwargs) -> Any:

    def _inner(cmd) -> Any:
        func = cmd.func if isinstance(cmd, SlashCommand) else cmd
        for name, desc in kwargs.items():
            try:
                func._param_desc_[name] = desc
            except AttributeError:
                func._param_desc_ = {name: desc}
        return cmd

    return _inner


def slash_command(**kwargs) -> Callable[[CmdT], SlashCommand]:

    def _inner(func: CmdT) -> SlashCommand:
        return SlashCommand(func, **kwargs)

    return _inner


def message_command(**kwargs) -> Callable[[MsgCmdT], MessageCommand]:

    def _inner(func: MsgCmdT) -> MessageCommand:
        return MessageCommand(func, **kwargs)

    return _inner


def user_command(**kwargs) -> Callable[[UsrCmdT], UserCommand]:

    def _inner(func: UsrCmdT) -> UserCommand:
        return UserCommand(func, **kwargs)

    return _inner


class _RangeMeta(type):

    @overload
    def __getitem__(cls: Type[RngT], max: int) -> Type[int]:
        ...

    @overload
    def __getitem__(cls: Type[RngT], max: tuple[int, int]) -> Type[int]:
        ...

    @overload
    def __getitem__(cls: Type[RngT], max: float) -> Type[float]:
        ...

    @overload
    def __getitem__(cls: Type[RngT], max: tuple[float, float]) -> Type[float]:
        ...

    def __getitem__(cls, max):
        return cls(*max) if isinstance(max, tuple) else cls(None, max)


class Range(metaclass=_RangeMeta):

    def __init__(self, min: NumT | None, max: NumT):
        if min is not None and min >= max:
            raise ValueError("`min` value must be lower than `max`")
        self.min = min
        self.max = max


class Bot(commands.Bot):

    application_id: int

    async def start(self, token: str, *, reconnect: bool = True) -> None:

        await self.login(token)

        app_info = await self.application_info()
        self._connection.application_id = app_info.id

        await self.sync_commands()
        await self.connect(reconnect=reconnect)

    def get_application_command(self, name: str) -> Command | None:

        for c in self.cogs.values():
            if isinstance(c, ApplicationCog):
                c = c._commands.get(name)
                if c:
                    return c

    async def delete_all_commands(self, guild_id: int | None = None):

        if guild_id is not None:
            await self.http.bulk_upsert_guild_commands(self.application_id, guild_id, [])
        else:
            await self.http.bulk_upsert_global_commands(self.application_id, [])

    async def delete_command(self, id: int, *, guild_id: int | None = None):

        if guild_id is not None:
            await self.http.delete_guild_command(self.application_id, guild_id, id)
        else:
            await self.http.delete_global_command(self.application_id, id)

    async def sync_commands(self) -> None:

        if not self.application_id:
            raise RuntimeError("sync_commands must be called after `run`, `start` or `login`")

        command_payloads = defaultdict(list)
        for cog in self.cogs.values():
            if not isinstance(cog, ApplicationCog):
                continue

            if not hasattr(cog, "_commands"):
                cog._commands = {}

            slashes = inspect.getmembers(cog, lambda c: isinstance(c, Command))
            for _, cmd in slashes:
                cmd.cog = cog
                cog._commands[cmd.name] = cmd
                body = cmd._build_command_payload()
                command_payloads[cmd.guild_id].append(body)

        global_commands = command_payloads.pop(None, [])
        if global_commands:
            await self.http.bulk_upsert_global_commands(self.application_id, global_commands)

        for guild_id, payload in command_payloads.items():
            await self.http.bulk_upsert_guild_commands(self.application_id, guild_id, payload)


class Context(Generic[BotT, CogT]):

    def __init__(self, bot: BotT, command: Command[CogT], interaction: discord.Interaction):
        self.bot = bot
        self.command = command
        self.interaction = interaction

    @overload
    def send(
        self,
        content: str = MISSING,
        *,
        embed: discord.Embed = MISSING,
        ephemeral: bool = MISSING,
        tts: bool = MISSING,
        view: discord.ui.View = MISSING,
        file: discord.File = MISSING
    ) -> Coroutine[Any, Any, discord.InteractionMessage | discord.WebhookMessage]:
        ...

    @overload
    def send(
        self,
        content: str = MISSING,
        *,
        embed: discord.Embed = MISSING,
        ephemeral: bool = MISSING,
        tts: bool = MISSING,
        view: discord.ui.View = MISSING,
        files: list[discord.File] = MISSING
    ) -> Coroutine[Any, Any, discord.InteractionMessage | discord.WebhookMessage]:
        ...

    @overload
    def send(
        self,
        content: str = MISSING,
        *,
        embeds: list[discord.Embed] = MISSING,
        ephemeral: bool = MISSING,
        tts: bool = MISSING,
        view: discord.ui.View = MISSING,
        file: discord.File = MISSING
    ) -> Coroutine[Any, Any, discord.InteractionMessage | discord.WebhookMessage]:
        ...

    @overload
    def send(
        self,
        content: str = MISSING,
        *,
        embeds: list[discord.Embed] = MISSING,
        ephemeral: bool = MISSING,
        tts: bool = MISSING,
        view: discord.ui.View = MISSING,
        files: list[discord.File] = MISSING
    ) -> Coroutine[Any, Any, discord.InteractionMessage | discord.WebhookMessage]:
        ...

    async def send(self, content=MISSING, **kwargs) -> discord.InteractionMessage | discord.WebhookMessage:

        if self.interaction.response.is_done():
            return await self.interaction.followup.send(content, wait=True, **kwargs)

        await self.interaction.response.send_message(content or None, **kwargs)

        return await self.interaction.original_message()

    async def reply(self, content=MISSING, **kwargs) -> discord.InteractionMessage | discord.WebhookMessage:
        return await self.send(content, **kwargs)

    async def defer(self, *, ephemeral: bool = False) -> None:
        await self.interaction.response.defer(ephemeral=ephemeral)

    @property
    def cog(self) -> CogT:
        return self.command.cog

    @property
    def guild(self) -> discord.Guild:
        return self.interaction.guild  # type: ignore

    @property
    def message(self) -> discord.Message:
        return self.interaction.message  # type: ignore

    @property
    def channel(self) -> discord.interactions.InteractionChannel:
        return self.interaction.channel  # type: ignore

    @property
    def author(self) -> discord.Member:
        return self.interaction.user  # type: ignore

    @property
    def voice_client(self) -> custom.Player | None:
        return self.guild.voice_client if self.guild else None  # type: ignore


class Command(Generic[CogT]):

    cog: CogT
    func: Callable
    name: str
    guild_id: int | None

    def _build_command_payload(self) -> dict[str, Any]:
        raise NotImplementedError

    def _build_arguments(self, interaction: discord.Interaction, state: discord.state.ConnectionState) -> dict[str, Any]:
        raise NotImplementedError

    async def invoke(self, context: Context[BotT, CogT], **params) -> None:
        await self.func(self.cog, context, **params)


class SlashCommand(Command[CogT]):

    def __init__(self, func: CmdT, **kwargs):

        self.func = func
        self.cog: CogT

        self.name: str = kwargs.get("name", func.__name__)

        self.description: str = kwargs.get("description") or func.__doc__ or "No description provided"

        self.guild_id: int | None = kwargs.get("guild_id")

        self.parameters = self._build_parameters()
        self._parameter_descriptions: dict[str, str] = defaultdict(lambda: "No description provided")

    def _build_arguments(self, interaction, state) -> dict[str, Any]:

        if 'options' not in interaction.data:
            return {}

        resolved = _parse_resolved_data(interaction, interaction.data.get('resolved'), state)
        result = {}
        for option in interaction.data['options']:
            value = option['value']
            if option['type'] in (6, 7, 8):
                value = resolved[int(value)]

            result[option['name']] = value
        return result

    def _build_parameters(self) -> dict[str, inspect.Parameter]:

        params = list(inspect.signature(self.func).parameters.values())
        try:
            params.pop(0)
        except IndexError:
            raise ValueError("expected argument `self` is missing")

        try:
            params.pop(0)
        except IndexError:
            raise ValueError("expected argument `context` is missing")

        return {p.name: p for p in params}

    def _build_descriptions(self) -> None:

        if not hasattr(self.func, '_param_desc_'):
            return

        for k, v in self.func._param_desc_.items():  # type: ignore
            if k not in self.parameters:
                raise TypeError(f"@describe used to describe a non-existent parameter `{k}`")

            self._parameter_descriptions[k] = v

    def _build_command_payload(self) -> dict[str, Any]:

        # sourcery no-metrics
        self._build_descriptions()

        payload: dict[str, Any] = {
            "name":        self.name,
            "description": self.description,
            "type":        1
        }

        params = self.parameters
        if params:
            options = []
            for name, param in params.items():
                ann = param.annotation

                if ann is param.empty:
                    raise TypeError(f"missing type annotation for parameter `{param.name}` for command `{self.name}`")

                if isinstance(ann, str):
                    ann = eval(ann)

                if isinstance(ann, Range):
                    real_t = type(ann.max)
                elif get_origin(ann) is Union:
                    args = get_args(ann)
                    real_t = args[0]
                elif get_origin(ann) is Literal:
                    real_t = type(ann.__args__[0])
                else:
                    real_t = ann

                typ = command_type_map[real_t]
                option: dict[str, Any] = {
                    'type':        typ,
                    'name':        name,
                    'description': self._parameter_descriptions[name]
                }
                if param.default is param.empty:
                    option['required'] = True

                if isinstance(ann, Range):
                    option['max_value'] = ann.max
                    option['min_value'] = ann.min

                elif get_origin(ann) is Union:
                    args = get_args(ann)

                    if not all(issubclass(k, discord.abc.GuildChannel) for k in args):
                        raise TypeError("Union parameter types only supported on *Channel types")

                    if len(args) != 3:
                        filtered = [channel_filter[i] for i in args]
                        option['channel_types'] = filtered

                elif get_origin(ann) is Literal:
                    arguments = ann.__args__
                    option['choices'] = [{'name': str(a), 'value': a} for a in arguments]

                elif issubclass(ann, discord.abc.GuildChannel):
                    option['channel_types'] = [channel_filter[ann]]

                options.append(option)
            options.sort(key=lambda f: not f.get('required'))
            payload['options'] = options
        return payload


class ContextMenuCommand(Command[CogT]):
    _type: ClassVar[int]

    def __init__(self, func: CtxMnT, **kwargs):
        self.func = func
        self.guild_id: int | None = kwargs.get('guild_id', None)
        self.name: str = kwargs.get('name', func.__name__)

    def _build_command_payload(self) -> dict[str, Any]:
        payload = {
            'name': self.name,
            'type': self._type
        }
        if self.guild_id is not None:
            payload['guild_id'] = self.guild_id
        return payload

    def _build_arguments(self, interaction: discord.Interaction, state: discord.state.ConnectionState) -> dict[str, Any]:
        resolved = _parse_resolved_data(interaction, interaction.data.get('resolved'), state)  # type: ignore
        value = resolved[int(interaction.data['target_id'])]  # type: ignore
        return {'target': value}

    async def invoke(self, context: Context[BotT, CogT], **params) -> None:
        await self.func(self.cog, context, *params.values())


class MessageCommand(ContextMenuCommand[CogT]):
    _type = 3


class UserCommand(ContextMenuCommand[CogT]):
    _type = 2


def _parse_resolved_data(interaction: discord.Interaction, data: dict[str, Any], state: discord.state.ConnectionState) -> dict[int, Any]:

    if not data:
        return {}

    assert interaction.guild

    resolved = {}

    resolved_users = data.get('users')
    if resolved_users:
        resolved_members = data['members']
        for id, d in resolved_users.items():
            member_data = resolved_members[id]
            member_data['user'] = d
            member = discord.Member(data=member_data, guild=interaction.guild, state=state)
            resolved[int(id)] = member

    resolved_channels = data.get('channels')
    if resolved_channels:
        for id, d in resolved_channels.items():
            d['position'] = None
            cls, _ = discord.channel._guild_channel_factory(d['type'])
            channel = cls(state=state, guild=interaction.guild, data=d)
            resolved[int(id)] = channel

    resolved_messages = data.get('messages')
    if resolved_messages:
        for id, d in resolved_messages.items():
            msg = discord.Message(state=state, channel=interaction.channel, data=d)  # type: ignore
            resolved[int(id)] = msg

    resolved_roles = data.get('roles')
    if resolved_roles:
        for id, d in resolved_roles.items():
            role = discord.Role(guild=interaction.guild, state=state, data=d)
            resolved[int(id)] = role

    return resolved


class ApplicationCog(commands.Cog, Generic[BotT]):

    def __init__(self, bot: BotT):
        self.bot: BotT = bot
        self._commands: dict[str, Command] = {}

    @commands.Cog.listener("on_interaction")
    async def _internal_interaction_handler(self, interaction: discord.Interaction):

        if interaction.type is not discord.InteractionType.application_command:
            return

        if not (command := self._commands.get(interaction.data["name"])):  # type: ignore
            return

        params: dict[str, Any] = command._build_arguments(interaction, self.bot._connection)

        ctx = Context(self.bot, command, interaction)
        try:
            await command.invoke(ctx, **params)
        except Exception as error:
            traceback.print_exception(type(error), error, error.__traceback__)
            if isinstance(error, exceptions.EmbedError):
                await ctx.send(embed=error.embed)
