# Future
from __future__ import annotations

# Standard Library
import datetime

# Packages
import discord
from discord.ext import commands

# My stuff
from cd.utilities import utils, values


class CDError(commands.CommandError):
    pass


class EmbedError(CDError):

    def __init__(
        self,
        *,
        # base
        colour: discord.Colour | None = values.MAIN,
        title: str | None = None,
        url: str | None = None,
        description: str | None = None,
        timestamp: datetime.datetime | None = None,
        # footer
        footer: str | None = None,
        footer_icon_url: str | None = None,
        # images
        image: str | None = None,
        thumbnail: str | None = None,
        # author
        author: str | None = None,
        author_url: str | None = None,
        author_icon_url: str | None = None,
        # extras
        emoji: str | None = None,
        view: discord.ui.View | None = None,
    ) -> None:

        self.embed: discord.Embed = utils.embed(
            colour=colour,
            title=title,
            url=url,
            description=description,
            timestamp=timestamp,
            footer=footer,
            footer_icon_url=footer_icon_url,
            image=image,
            thumbnail=thumbnail,
            author=author,
            author_url=author_url,
            author_icon_url=author_icon_url,
            emoji=emoji,
        )
        self.view: discord.ui.View | None = view
