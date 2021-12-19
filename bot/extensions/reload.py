# Future
from __future__ import annotations

# Standard Library
import logging
import os
import pathlib
from typing import Any

# Packages
from discord.ext import commands, tasks

# My stuff
from core.bot import CD


def path_from_extension(extension: str) -> pathlib.Path:
    return pathlib.Path(extension.replace(".", os.sep) + ".py")


def setup(bot: CD):
    bot.add_cog(Reload(bot=bot))


IGNORE_EXTENSIONS = [
    "jishaku"
]
__log__: logging.Logger = logging.getLogger("bot.extensions.reload")


class Reload(commands.Cog):

    def __init__(self, bot: CD) -> None:
        self.bot: CD = bot
        self.last_modified_time: dict[Any, Any] = {}

        self.reload_loop.start()

    def cog_unload(self) -> None:
        self.reload_loop.stop()

    #

    @tasks.loop(seconds=3)
    async def reload_loop(self) -> None:

        for extension in list(self.bot.extensions.keys()):

            if extension in IGNORE_EXTENSIONS:
                continue

            time = os.path.getmtime(path_from_extension(extension))

            try:
                if self.last_modified_time[extension] == time:
                    continue
            except KeyError:
                self.last_modified_time[extension] = time

            try:
                self.bot.reload_extension(extension)
            except commands.ExtensionError:
                __log__.error(f"[EXTENSIONS] Failed reload - {extension}")
            else:
                __log__.info(f"[EXTENSIONS] Reloaded - {extension}")
            finally:
                self.last_modified_time[extension] = time

    @reload_loop.before_loop
    async def before_reload_loop(self) -> None:

        for extension in self.bot.extensions.keys():

            if extension in IGNORE_EXTENSIONS:
                continue

            self.last_modified_time[extension] = os.path.getmtime(path_from_extension(extension))
