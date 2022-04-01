# Future
from __future__ import annotations

# Standard Library
from typing import TypeVar

# Packages
import discord
from discord.ext import commands

# Local
# My
from cd import custom, exceptions


__all__ = (
    "EnumConverter",
)


EnumType = TypeVar("EnumType", bound=discord.Enum)
NL = "\n"


class EnumConverter(commands.Converter[EnumType]):

    def __init__(self, enum: type[EnumType], name: str) -> None:
        self.enum: type[EnumType] = enum
        self.name: str = name

    async def convert(self, ctx: custom.Context, argument: str) -> EnumType:  # pyright: reportIncompatibleMethodOverride=false

        if enum := getattr(self.enum, argument.replace(" ", "_").upper(), None):
            return enum

        options = [f"- **{option}**" for option in [repeat_type.name.replace("_", " ").lower() for repeat_type in self.enum]]
        raise exceptions.EmbedError(description=f"**{self.name}** must be one of:\n{NL.join(options)}")
