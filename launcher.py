import asyncio

import jishaku

from cd import logger
from cd.bot import CD
from cd.config import CONFIG

# jishaku
jishaku.Flags.HIDE = True
jishaku.Flags.NO_UNDERSCORE = True
jishaku.Flags.NO_DM_TRACEBACK = True

# logging
logger.setup()

# bot
bot = CD()


async def main() -> None:
    async with bot:
        await bot.start(CONFIG.discord.token)


asyncio.run(main())
