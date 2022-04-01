# Future
from __future__ import annotations

# Standard Library
import datetime
from typing import Any

# Packages
import discord

# Local
from cd import custom, utilities, values
from cd.paginators.base import BasePaginator


__all__ = (
    "EmbedPaginator",
)


class EmbedPaginator(BasePaginator):

    def __init__(
        self,
        *,
        # base
        ctx: custom.Context,
        entries: list[Any],
        per_page: int,
        start_page: int = 0,
        timeout: int = 300,
        edit_message: bool = True,
        delete_message: bool = False,
        codeblock: bool = False,
        splitter: str = "\n",
        # embed-paginator-specific
        header: str | None = None,
        footer: str | None = None,
        colour: discord.Colour = values.MAIN,
        title: str | None = None,
        url: str | None = None,
        embed_timestamp: datetime.datetime | None = None,
        embed_footer: str | None = None,
        embed_footer_icon_url: str | None = None,
        image: str | None = None,
        thumbnail: str | None = None,
        author: str | None = None,
        author_url: str | None = None,
        author_icon_url: str | None = None,
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

        self.embed: discord.Embed = utilities.embed(
            colour=colour,
            title=title,
            url=url,
            timestamp=embed_timestamp,
            footer=embed_footer,
            footer_icon_url=embed_footer_icon_url,
            image=image,
            thumbnail=thumbnail,
            author=author,
            author_url=author_url,
            author_icon_url=author_icon_url,
        )

    async def _update_page(self) -> None:
        self.embed.description = f"{self.CODEBLOCK_START}{self.header}{self.pages[self.page]}{self.footer}{self.CODEBLOCK_END}"
