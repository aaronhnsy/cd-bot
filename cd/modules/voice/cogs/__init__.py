from __future__ import annotations

from typing import TYPE_CHECKING

from .effects import *
from .player import *

if TYPE_CHECKING:
    from cd.bot import CD


async def setup(bot: CD) -> None:
    await bot.add_cog(Effects(bot))
    await bot.add_cog(Player(bot))
