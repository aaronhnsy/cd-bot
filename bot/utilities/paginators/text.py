# Future
from __future__ import annotations

# Standard Library
from typing import Any

# My stuff
from utilities import custom, paginators


__all__ = (
    "TextPaginator",
)


class TextPaginator(paginators.BasePaginator):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        entries: list[Any],
        per_page: int,
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
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
            codeblock=codeblock,
            splitter=splitter,
        )

        self.header: str = header or ""
        self.footer: str = footer or ""

    async def set_page(self, page: int) -> None:
        self.content = f"{self.CODEBLOCK_START}{self.header}{self.pages[page]}{self.footer}{self.CODEBLOCK_END}"
