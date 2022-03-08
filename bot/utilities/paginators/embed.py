# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import discord

# My stuff
from core import values
from utilities import custom, paginators, utils


__all__ = (
    "EmbedPaginator",
)


class EmbedPaginator(paginators.BasePaginator):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        entries: list[Any],
        per_page: int,
        start_page: int = 0,
        timeout: int = 300,
        edit_message: bool = True,
        delete_message: bool = False,
        codeblock: bool = False,
        splitter: str = "\n",
        header: str | None = None,
        footer: str | None = None,
        embed_footer: str | None = None,
        embed_footer_url: str | None = None,
        image: str | None = None,
        thumbnail: str | None = None,
        author: str | None = None,
        author_url: str | None = None,
        author_icon_url: str | None = None,
        title: str | None = None,
        url: str | None = None,
        colour: discord.Colour = values.MAIN,
    ) -> None:

        super().__init__(
            ctx=ctx,
            entries=entries,
            per_page=per_page,
            start_page=start_page,
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
            codeblock=codeblock,
            splitter=splitter,
        )

        self.header: str = header or ""
        self.footer: str = footer or ""

        self.embed_footer: str | None = embed_footer
        self.embed_footer_url: str | None = embed_footer_url

        self.embed_image: str | None = image
        self.embed_thumbnail: str | None = thumbnail

        self.embed_author: str | None = author
        self.embed_author_url: str | None = author_url
        self.embed_author_icon_url: str | None = author_icon_url

        self.embed_title: str | None = title
        self.embed_url: str | None = url

        self.embed_colour: discord.Colour = colour

        self.embed: discord.Embed = utils.embed(
            footer=embed_footer,
            footer_url=embed_footer_url,
            image=image,
            thumbnail=thumbnail,
            author=author,
            author_url=author_url,
            author_icon_url=author_icon_url,
            title=title,
            url=url,
            colour=colour,
        )

    #

    async def _update_page(self) -> None:
        self.embed.description = f"{self.CODEBLOCK_START}{self.header}{self.pages[self.page]}{self.footer}{self.CODEBLOCK_END}"
