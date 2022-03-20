# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import discord

# My stuff
from cd import custom
from cd.paginators.base import BasePaginator


__all__ = (
    "EmbedsPaginator",
)


class EmbedsPaginator(BasePaginator):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        entries: list[Any],
        start_page: int = 0,
        timeout: int = 300,
        edit_message: bool = False,
        delete_message: bool = False,
    ) -> None:

        super().__init__(
            ctx=ctx,
            entries=entries,
            per_page=1,
            start_page=start_page,
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
            join_pages=False
        )

        self.embed: discord.Embed | None = None

    #

    async def _update_page(self) -> None:
        self.embed = self.pages[self.page]
