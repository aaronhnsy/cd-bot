# Standard Library
from typing import TYPE_CHECKING, Any, TypeAlias


if TYPE_CHECKING:
    # Libraries
    from discord.ext import commands

    # Project
    from cd import custom

    # Local Folder
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
