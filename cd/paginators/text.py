from __future__ import annotations

from typing import Any

from cd import custom, values
from cd.paginators.base import BasePaginator


__all__ = (
    "TextPaginator",
)


class TextPaginator(BasePaginator):

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
        # text paginator specific
        header: str | None = None,
        footer: str | None = None,
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

    async def update_state(self) -> None:
        self.content = f"{self.CODEBLOCK_START}{self.header}{self.pages[self.page]}{self.footer}{self.CODEBLOCK_END}"
