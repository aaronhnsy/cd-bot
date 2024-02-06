from __future__ import annotations

from typing import TYPE_CHECKING

from .controls import *
from .effects import *


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = ["setup"]


async def setup(bot: CD) -> None:
    await bot.add_cog(VoiceControls(bot))
    await bot.add_cog(VoiceEffects(bot))
