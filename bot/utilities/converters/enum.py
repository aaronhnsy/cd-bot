# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Generic, Type, TypeVar

# Packages
import discord
from discord.ext import commands

# My stuff
from core import values
from utilities import exceptions


if TYPE_CHECKING:
    # My stuff
    from core.bot import CD


__all__ = (
    "EnumConverter",
)


EnumType = TypeVar("EnumType", bound=discord.Enum)


class EnumConverter(Generic[EnumType], commands.Converter[EnumType]):

    def __init__(self, enum: Type[EnumType], name: str) -> None:
        self.enum: Type[EnumType] = enum
        self.name: str = name

    async def convert(self, ctx: commands.Context[CD], argument: str) -> EnumType:

        if enum := getattr(self.enum, argument.replace(" ", "_").upper(), None):
            return enum

        options = [f"- **{option}**" for option in [repeat_type.name.replace("_", " ").lower() for repeat_type in self.enum]]

        raise exceptions.EmbedError(
            colour=values.RED,
            description=f"**{self.name}** must be one of:\n{values.NL.join(options)}",
        )
