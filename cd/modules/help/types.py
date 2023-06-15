from typing import Any, TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from discord.ext import commands
    from cd import custom
    from .command import HelpCommandCategory


__all__ = [
    "SingleCommand",
    "GroupCommand",
    "Command",
    "HelpCommandCategories",
]


SingleCommand: TypeAlias = "commands.Command[custom.Cog, Any, Any] | commands.Command[None, Any, Any]"
GroupCommand: TypeAlias = "commands.Group[custom.Cog, Any, Any] | commands.Group[None, Any, Any]"
Command: TypeAlias = "SingleCommand | GroupCommand"

HelpCommandCategories: TypeAlias = "dict[str, HelpCommandCategory]"
