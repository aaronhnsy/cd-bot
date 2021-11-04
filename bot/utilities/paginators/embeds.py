# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import discord

# My stuff
from utilities import custom, paginators


__all__ = (
    "EmbedsPaginator",
)


class EmbedsPaginator(paginators.BasePaginator):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        entries: list[Any],
        timeout: int = 300,
        edit_message: bool = False,
        delete_message: bool = False,
    ) -> None:

        super().__init__(
            ctx=ctx,
            entries=entries,
            per_page=1,
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
            join_pages=False
        )

        self.embed: discord.Embed | None = None

    async def set_page(self, page: int) -> None:
        self.embed = self.pages[page]
