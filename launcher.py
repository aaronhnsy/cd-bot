from __future__ import annotations

import asyncio

import jishaku

from cd.bot import CD
from cd.config import DISCORD_TOKEN
from cd.utilities.logging import setup_logger


setup_logger()

jishaku.Flags.HIDE = True
jishaku.Flags.NO_UNDERSCORE = True
jishaku.Flags.NO_DM_TRACEBACK = True

bot: CD = CD()


async def main() -> None:

    async with bot:
        await bot.start(token=DISCORD_TOKEN)


asyncio.run(main())
