
# Standard Library
from typing import TYPE_CHECKING

# Libraries
from discord.ext import commands


if TYPE_CHECKING:
    # Project
    from cd.bot import CD  # type: ignore
    from cd.modules.voice.custom.player import Player


__all__ = ["Context"]


class Context(commands.Context["CD"]):

    @property
    def player(self) -> Player | None:
        return self.guild.voice_client if self.guild else None  # type: ignore
