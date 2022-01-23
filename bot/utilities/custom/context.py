# Future
from __future__ import annotations

# Standard Library
import functools
import io
from typing import TYPE_CHECKING, Any

# Packages
import discord
from discord.ext import commands

# My stuff
from core import values
from utilities import custom, paginators


if TYPE_CHECKING:

    # My stuff
    # noinspection PyUnresolvedReferences
    from core.bot import CD


__all__ = (
    "Context",
)


class Context(commands.Context["CD"]):

    # Properties

    @property
    def voice_client(self) -> custom.Player | None:
        return self.guild.voice_client if self.guild else None  # type: ignore

    # Paginators

    async def paginate_text(
        self,
        *,
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
    ) -> paginators.TextPaginator:

        paginator = paginators.TextPaginator(
            ctx=self,
            entries=entries,
            per_page=per_page,
            start_page=start_page,
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
            codeblock=codeblock,
            splitter=splitter,
            header=header,
            footer=footer,
        )
        await paginator.start()

        return paginator

    async def paginate_embed(
        self,
        *,
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
        embed_footer: str | None = None,
        embed_footer_url: str | None = None,
        image: str | None = None,
        thumbnail: str | None = None,
        author: str | None = None,
        author_url: str | None = None,
        author_icon_url: str | None = None,
        title: str | None = None,
        url: str | None = None,
        colour: discord.Colour = values.MAIN,
    ) -> paginators.EmbedPaginator:

        paginator = paginators.EmbedPaginator(
            ctx=self,
            entries=entries,
            per_page=per_page,
            start_page=start_page,
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
            codeblock=codeblock,
            splitter=splitter,
            header=header,
            footer=footer,
            embed_footer=embed_footer,
            embed_footer_url=embed_footer_url,
            image=image,
            thumbnail=thumbnail,
            author=author,
            author_url=author_url,
            author_icon_url=author_icon_url,
            title=title,
            url=url,
            colour=colour,
        )
        await paginator.start()

        return paginator

    async def paginate_fields(
        self,
        *,
        entries: list[tuple[Any, Any]],
        per_page: int,
        start_page: int = 0,
        timeout: int = 300,
        edit_message: bool = True,
        delete_message: bool = False,
        codeblock: bool = False,
        splitter: str = "\n",
        header: str | None = None,
        footer: str | None = None,
        embed_footer: str | None = None,
        embed_footer_url: str | None = None,
        image: str | None = None,
        thumbnail: str | None = None,
        author: str | None = None,
        author_url: str | None = None,
        author_icon_url: str | None = None,
        title: str | None = None,
        url: str | None = None,
        colour: discord.Colour = values.MAIN,
    ) -> paginators.FieldsPaginator:

        paginator = paginators.FieldsPaginator(
            ctx=self,
            entries=entries,
            per_page=per_page,
            start_page=start_page,
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
            codeblock=codeblock,
            splitter=splitter,
            header=header,
            footer=footer,
            embed_footer=embed_footer,
            embed_footer_url=embed_footer_url,
            image=image,
            thumbnail=thumbnail,
            author=author,
            author_url=author_url,
            author_icon_url=author_icon_url,
            title=title,
            url=url,
            colour=colour,
        )
        await paginator.start()

        return paginator

    async def paginate_embeds(
        self,
        *,
        entries: list[discord.Embed],
        start_page: int = 0,
        timeout: int = 300,
        edit_message: bool = True,
        delete_message: bool = True,
    ) -> paginators.EmbedsPaginator:

        paginator = paginators.EmbedsPaginator(
            ctx=self,
            entries=entries,
            start_page=start_page,
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
        )
        await paginator.start()

        return paginator

    async def paginate_file(
        self,
        *,
        entries: list[functools.partial[bytes | io.BytesIO]],
        start_page: int = 0,
        timeout: int = 300,
        edit_message: bool = True,
        delete_message: bool = True,
        header: str | None = None
    ) -> paginators.FilePaginator:

        paginator = paginators.FilePaginator(
            ctx=self,
            entries=entries,
            start_page=start_page,
            timeout=timeout,
            edit_message=edit_message,
            delete_message=delete_message,
            header=header
        )
        await paginator.start()

        return paginator

    # Misc

    async def try_dm(self, *args: Any, **kwargs: Any) -> discord.Message | None:

        try:
            return await self.author.send(*args, **kwargs)
        except (discord.HTTPException, discord.Forbidden):
            try:
                return await self.reply(*args, **kwargs)
            except (discord.HTTPException, discord.Forbidden):
                return None
