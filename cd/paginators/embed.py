from __future__ import annotations

import datetime
from typing import Any

import discord

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
        join_entries: bool = True,
        codeblock: bool = False,
        splitter: str = "\n",
        edit_message_when_done: bool = True,
        delete_message_when_done: bool = False,
        timeout: int | None = 300,
        # embed paginator specific
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
            join_entries=join_entries,
            codeblock=codeblock,
            splitter=splitter,
            edit_message_when_done=edit_message_when_done,
            delete_message_when_done=delete_message_when_done,
            timeout=timeout,
        )

        self.CODEBLOCK_START: str = values.CODEBLOCK_START if self.codeblock else ""
        self.CODEBLOCK_END: str = values.CODEBLOCK_END if self.codeblock else ""

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

    async def update_state(self) -> None:
        self.embed.description = f"{self.CODEBLOCK_START}{self.header}{self.pages[self.page]}{self.footer}{self.CODEBLOCK_END}"
