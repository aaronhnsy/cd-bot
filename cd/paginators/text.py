# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Local
from cd import custom
from cd.paginators.base import BasePaginator


__all__ = (
    "TextPaginator",
)


class TextPaginator(BasePaginator):

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

    #

    async def _update_page(self) -> None:
        self.content = f"{self.CODEBLOCK_START}{self.header}{self.pages[self.page]}{self.footer}{self.CODEBLOCK_END}"
