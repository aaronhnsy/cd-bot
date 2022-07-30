from __future__ import annotations

import discord

from cd import custom
from cd.paginators.base import BasePaginator


__all__ = (
    "EmbedsPaginator",
)


class EmbedsPaginator(BasePaginator):

    def __init__(
        self,
        *,
        # base
        ctx: custom.Context,
        entries: list[discord.Embed],
        start_page: int = 0,
        edit_message_when_done: bool = True,
        delete_message_when_done: bool = False,
        timeout: int | None = 300,
    ) -> None:

        super().__init__(
            ctx=ctx,
            entries=entries,
            per_page=1,
            start_page=start_page,
            edit_message_when_done=edit_message_when_done,
            delete_message_when_done=delete_message_when_done,
            timeout=timeout,
        )

    async def update_state(self) -> None:
        self.embed = self.pages[self.page]
