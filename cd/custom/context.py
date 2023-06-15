from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from cd.bot import CD


__all__ = ["Context"]


class Context(commands.Context["CD"]):
    pass
