from typing import Unpack

import discord
from discord.ext import commands

from cd import utilities


__all__ = ["EmbedError"]


class EmbedError(commands.CommandError):

    def __init__(self, view: discord.ui.View | None = None, **kwargs: Unpack[utilities.EmbedParameters]) -> None:
        self.embed: discord.Embed = utilities.embed(**kwargs)
        self.view: discord.ui.View | None = view
