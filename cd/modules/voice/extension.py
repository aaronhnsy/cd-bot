# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Local
from cd.modules.voice.cogs import Effects, Play, Player, Queue


if TYPE_CHECKING:
    # Local
    from cd.bot import SkeletonClique


__all__ = (
    "setup",
)


async def setup(bot: SkeletonClique) -> None:
    await bot.add_cog(Effects(bot))
    await bot.add_cog(Play(bot))
    await bot.add_cog(Player(bot))
    await bot.add_cog(Queue(bot))
