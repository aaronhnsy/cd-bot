from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import lava


if TYPE_CHECKING:
    from cd.bot import CD  # type: ignore


__all__ = ["Player"]
    

class Player(lava.Player["CD"]):
    pass
