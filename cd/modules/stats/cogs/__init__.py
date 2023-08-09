from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Local Folder
from .commands import *
from .events import *


if TYPE_CHECKING:
    # Project
    from cd.bot import CD


async def setup(bot: CD) -> None:
    await bot.add_cog(StatsCommands(bot))
    await bot.add_cog(StatsEvents(bot))
