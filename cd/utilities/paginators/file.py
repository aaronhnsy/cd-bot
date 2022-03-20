# Future
from __future__ import annotations

# Standard Library
import functools
import io

# My stuff
from cd.utilities import custom, paginators, utils


__all__ = (
    "FilePaginator",
)


class FilePaginator(paginators.BasePaginator):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        entries: list[functools.partial[bytes | io.BytesIO]],
        start_page: int = 0,
        timeout: int = 300,
        edit_message: bool = True,
        delete_message: bool = False,
        header: str | None = None,
    ) -> None:

        super().__init__(
            ctx=ctx,
            entries=entries,
            per_page=1,
            start_page=start_page,
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
        )

        self.header: str = header or ""

    #

    async def _update_page(self) -> None:

        buffer = await self.entries[self.page]()
        url = await utils.upload_file(self.ctx.bot.session, file=buffer, format="png")
        buffer.close()

        self.content = f"{self.header}{url}"
