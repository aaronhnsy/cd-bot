# Future
from __future__ import annotations

# Standard Library
import asyncio
import os

# My stuff
from core import config
from core.bot import CD
from utilities.logger import setup_logger


setup_logger()


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"


async def main() -> None:

    bot = CD()

    async with bot:
        await bot.start(token=config.TOKEN)


asyncio.run(main())
