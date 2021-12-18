# Future
from __future__ import annotations

# Standard Library
import functools
import io

# My stuff
from utilities import custom, paginators, utils


__all__ = (
    "FilePaginator",
)


class FilePaginator(paginators.BasePaginator):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        entries: list[functools.partial[bytes | io.BytesIO]],
        timeout: int = 300,
        edit_message: bool = True,
        delete_message: bool = False,
        header: str | None = None,
    ) -> None:

        super().__init__(
            ctx=ctx,
            entries=entries,
            per_page=1,
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
        )

        self.header: str = header or ""

    async def set_page(self, page: int) -> None:

        buffer = await self.entries[page]()
        url = await utils.upload_file(self.ctx.bot.session, file=buffer, format="png")
        buffer.close()

        self.content = f"{self.header}{url}"
