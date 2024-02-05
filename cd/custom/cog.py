from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = ["Cog"]


class Cog(commands.Cog):
    emoji: str = "\N{WHITE QUESTION MARK ORNAMENT}"
    description: str = "No description provided."  # type: ignore

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot
