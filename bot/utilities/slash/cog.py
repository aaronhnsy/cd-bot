# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Packages
from discord.ext import commands


if TYPE_CHECKING:
    # My stuff
    from core.bot import CD


__all__ = (
    "ApplicationCog",
)


class ApplicationCog(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot
