from __future__ import annotations

import asyncio

import jishaku

from cd.bot import SkeletonClique
from cd.config import DISCORD_TOKEN
from cd.utilities.logging import setup_logger


setup_logger()

jishaku.Flags.HIDE = True
jishaku.Flags.NO_UNDERSCORE = True
jishaku.Flags.NO_DM_TRACEBACK = True

bot: SkeletonClique = SkeletonClique()


async def main() -> None:

    async with bot:
        await bot.start(token=DISCORD_TOKEN)


asyncio.run(main())
