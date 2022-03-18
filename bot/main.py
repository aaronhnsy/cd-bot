# Future
from __future__ import annotations

# Standard Library
import asyncio

# My stuff
from core import bot, config
from utilities.logger import setup_logger


setup_logger()


async def main() -> None:

    CD = bot.CD()

    async with CD:
        await CD.start(config.TOKEN)


asyncio.run(main())
