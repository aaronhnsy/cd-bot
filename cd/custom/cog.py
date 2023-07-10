from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Libraries
from discord.ext import commands


if TYPE_CHECKING:
    # Project
    from cd.bot import CD


__all__ = ["Cog"]


class Cog(commands.Cog):
    emoji: str = "\N{WHITE QUESTION MARK ORNAMENT}"
    description: str = "No description provided."  # pyright: ignore - idc about incorrectly overriding this

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot
