from __future__ import annotations

from typing import TYPE_CHECKING

from .effects import *
from .events import *
from .player import *


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = ["setup"]


async def setup(bot: CD) -> None:
    await bot.add_cog(VoicePlayer(bot))
    await bot.add_cog(VoiceEvents(bot))
    await bot.add_cog(VoiceEffects(bot))
