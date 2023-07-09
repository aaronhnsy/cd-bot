# Standard Library
from typing import TYPE_CHECKING

# Libraries
from discord.ext import commands


if TYPE_CHECKING:
    # Project
    from cd.bot import CD  # type: ignore


__all__ = ["Context"]


class Context(commands.Context["CD"]):
    pass
