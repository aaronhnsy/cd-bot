# Future
from __future__ import annotations

# Packages
import discord
from discord.ext import commands

# My stuff
from utilities import utils


class CDError(commands.CommandError):
    pass


class EmbedError(CDError):

    def __init__(
        self,
        *,
        footer: str | None = None,
        footer_url: str | None = None,
        image: str | None = None,
        thumbnail: str | None = None,
        author: str | None = None,
        author_url: str | None = None,
        author_icon_url: str | None = None,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
        colour: discord.Colour | None = None,
        emoji: str | None = None,
        view: discord.ui.View | None = None,
    ) -> None:

        if colour is None:
            colour = discord.Colour.red()

        self.embed: discord.Embed = utils.embed(
            footer_url=footer_url,
            footer=footer,
            image=image,
            thumbnail=thumbnail,
            author=author,
            author_url=author_url,
            author_icon_url=author_icon_url,
            title=title,
            description=description,
            url=url,
            colour=colour,
            emoji=emoji,
        )
        self.view: discord.ui.View | None = view
