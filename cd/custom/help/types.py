# Standard Library
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

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


type Cog = custom.Cog

type SingleCommand = commands.Command[Cog, Any, Any] | commands.Command[None, Any, Any]
type GroupCommand = commands.Group[Cog, Any, Any] | commands.Group[None, Any, Any]
type Command = SingleCommand | GroupCommand
type BotCommandMapping = Mapping[Cog | None, list[Command]]

type HelpCommandCategories = dict[str, HelpCommandCategory]
