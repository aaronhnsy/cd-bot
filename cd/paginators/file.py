from __future__ import annotations

import functools
import io
from collections.abc import Coroutine
from typing import Any

from cd import custom, utilities
from cd.paginators.base import BasePaginator


__all__ = (
    "FilePaginator",
)


class FilePaginator(BasePaginator):

    def __init__(
        self,
        *,
        # base
        ctx: custom.Context,
        entries: list[functools.partial[Coroutine[Any, Any, io.BytesIO]]],
        start_page: int = 0,
        edit_message_when_done: bool = True,
        delete_message_when_done: bool = False,
        timeout: int | None = 300,
        # file paginator specific
        header: str | None = None,
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

        self.header: str = header or ""
        self._cache: dict[int, str] = {}

    async def update_state(self) -> None:

        if not (url := self._cache.get(self.page)):
            buffer = await self.entries[self.page]()
            url = await utilities.upload_file(self.ctx.bot.session, fp=buffer, format="png")
            buffer.close()
            self._cache[self.page] = url

        self.content = f"{self.header}{url}"
