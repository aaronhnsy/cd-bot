from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Local Folder
from .effects import *
from .player import *


if TYPE_CHECKING:
    # Project
    from cd.bot import CD


async def setup(bot: CD) -> None:
    await bot.add_cog(Effects(bot))
    await bot.add_cog(Player(bot))
