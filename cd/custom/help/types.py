from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypedDict

from discord.ext import commands, paginators

from cd import custom


if TYPE_CHECKING:
    from .controller import HelpCommandController, HelpCommandControllerSelect


__all__ = [
    "SingleCommand",
    "GroupCommand",
    "Command",
    "BotCommandMapping",
    "HelpCommandControllerItems",
    "HelpCommandCategory",
    "HelpCommandCategories",
]


type SingleCommand = commands.Command[custom.Cog, Any, Any] | commands.Command[None, Any, Any]
type GroupCommand = commands.Group[custom.Cog, Any, Any] | commands.Group[None, Any, Any]
type Command = SingleCommand | GroupCommand
type BotCommandMapping = Mapping[custom.Cog | None, list[Command]]


class HelpCommandControllerItems(TypedDict):
    select: HelpCommandControllerSelect
    first: paginators.FirstPageButton[HelpCommandController]
    previous: paginators.PreviousPageButton[HelpCommandController]
    label: paginators.LabelButton[HelpCommandController]
    next: paginators.NextPageButton[HelpCommandController]
    last: paginators.LastPageButton[HelpCommandController]
    stop: paginators.StopButton[HelpCommandController]


@dataclasses.dataclass
class HelpCommandCategory:
    name: str
    description: str
    emoji: str
    fields: list[tuple[str, str, bool]]


type HelpCommandCategories = dict[str, HelpCommandCategory]
