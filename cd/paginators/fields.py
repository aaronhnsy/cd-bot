from __future__ import annotations

import datetime
from typing import Any

import discord

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
        entries: list[tuple[Any, Any, bool]],
        per_page: int,
        start_page: int = 0,
        edit_message_when_done: bool = True,
        delete_message_when_done: bool = False,
        timeout: int | None = 300,
        # field paginator specific
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
            join_entries=False,
            edit_message_when_done=edit_message_when_done,
            delete_message_when_done=delete_message_when_done,
            timeout=timeout,
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

    async def update_state(self) -> None:

        self.embed.clear_fields()

        for name, value, inline in self.pages[self.page]:
            self.embed.add_field(name=name, value=value, inline=inline)
