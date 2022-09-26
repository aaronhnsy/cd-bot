from __future__ import annotations

from typing import TYPE_CHECKING

from .economy import *
from .events import *


if TYPE_CHECKING:
    from cd.bot import CD


async def setup(bot: CD) -> None:
    await bot.add_cog(Economy(bot))
    await bot.add_cog(EconomyEvents(bot))
