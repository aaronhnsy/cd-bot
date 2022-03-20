# Future
from __future__ import annotations

# Standard Library
import datetime
from typing import Any

# Packages
import discord

# My stuff
from cd import custom, utilities, values
from cd.paginators.base import BasePaginator


__all__ = (
    "FieldsPaginator",
)


class FieldsPaginator(BasePaginator):

    def __init__(
        self,
        *,
        # base
        ctx: custom.Context,
        entries: list[tuple[Any, Any]],
        per_page: int,
        start_page: int = 0,
        timeout: int = 300,
        edit_message: bool = True,
        delete_message: bool = False,
        codeblock: bool = False,
        splitter: str = "\n",
        # field-paginator-specific
        embed_colour: discord.Colour | None = values.MAIN,
        embed_title: str | None = None,
        embed_url: str | None = None,
        embed_description: str | None = None,
        embed_timestamp: datetime.datetime | None = None,
        embed_footer: str | None = None,
        embed_footer_icon_url: str | None = None,
        embed_image: str | None = None,
        embed_thumbnail: str | None = None,
        embed_author: str | None = None,
        embed_author_url: str | None = None,
        embed_author_icon_url: str | None = None,

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
            join_pages=False
        )

        self.embed: discord.Embed = utilities.embed(
            colour=embed_colour,
            title=embed_title,
            url=embed_url,
            description=embed_description,
            timestamp=embed_timestamp,
            footer=embed_footer,
            footer_icon_url=embed_footer_icon_url,
            image=embed_image,
            thumbnail=embed_thumbnail,
            author=embed_author,
            author_url=embed_author_url,
            author_icon_url=embed_author_icon_url,
        )

    async def _update_page(self) -> None:

        self.embed.clear_fields()

        for name, value in self.pages[self.page]:
            self.embed.add_field(name=name, value=value, inline=False)
