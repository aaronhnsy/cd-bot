# Future
from __future__ import annotations

# Standard Library
import logging
import os
import pathlib

# Packages
from discord.ext import commands, tasks

# Local
from cd.bot import CD


__log__: logging.Logger = logging.getLogger("cd.extensions.reloader")


async def setup(bot: CD):
    await bot.add_cog(Reloader(bot=bot))


class Reloader(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot

        self.last_modified_times: dict[str, float] = {}

    async def cog_load(self) -> None:
        self.reload_loop.start()

    async def cog_unload(self) -> None:
        self.reload_loop.stop()

    @staticmethod
    def get_modified_time(extension: str) -> float:
        return os.path.getmtime(pathlib.Path(extension.replace(".", os.sep) + ".py"))

    @tasks.loop(seconds=3)
    async def reload_loop(self) -> None:

        for extension in list(self.bot.extensions.keys()):

            if extension in ["jishaku"]:
                continue

            modified_time = self.get_modified_time(extension)
            last_modified_time = self.last_modified_times.setdefault(extension, modified_time)

            if modified_time == last_modified_time:
                continue

            try:
                await self.bot.reload_extension(extension)
            except commands.ExtensionError:
                __log__.error(f"[EXTENSIONS] Reload failed - {extension}")
            else:
                __log__.info(f"[EXTENSIONS] Reloaded - {extension}")

            self.last_modified_times[extension] = modified_time

    @reload_loop.before_loop
    async def before_reload_loop(self) -> None:

        for extension in self.bot.extensions.keys():

            if extension in ["jishaku"]:
                continue

            self.last_modified_times[extension] = self.get_modified_time(extension)
