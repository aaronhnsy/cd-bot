# Standard Library
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeAlias

# Libraries
from discord.ext import commands

# Project
from cd import custom


if TYPE_CHECKING:
    # Local Folder
    from .command import HelpCommandCategory


__all__ = [
    "Cog",
    "SingleCommand",
    "GroupCommand",
    "Command",
    "BotCommandMapping",
    "HelpCommandCategories",
]


Cog: TypeAlias = custom.Cog

SingleCommand: TypeAlias = commands.Command[Cog, Any, Any] | commands.Command[None, Any, Any]
GroupCommand: TypeAlias = commands.Group[Cog, Any, Any] | commands.Group[None, Any, Any]
Command: TypeAlias = SingleCommand | GroupCommand
BotCommandMapping: TypeAlias = Mapping[Cog | None, list[Command]]

HelpCommandCategories: TypeAlias = dict[str, "HelpCommandCategory"]
