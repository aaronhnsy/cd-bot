from __future__ import annotations

from typing import TYPE_CHECKING

from .commands import *
from .events import *


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = ["setup"]


async def setup(bot: CD) -> None:
    await bot.add_cog(StatsCommands(bot))
    await bot.add_cog(StatsEvents(bot))
