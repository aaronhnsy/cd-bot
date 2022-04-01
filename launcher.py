# Future
from __future__ import annotations

# Standard Library
import asyncio
import os

# Local
from cd.bot import CD
from cd.config import TOKEN
from cd.utilities.logger import setup_logger


setup_logger()

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"

bot = CD()


async def main() -> None:

    async with bot:
        await bot.start(token=TOKEN)


asyncio.run(main())
