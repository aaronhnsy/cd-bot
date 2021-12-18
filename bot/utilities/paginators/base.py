# Future
from __future__ import annotations

# Standard Library
import abc
from typing import Any

# Packages
import discord

# My stuff
from core import values
from utilities import custom


__all__ = (
    "PaginatorButtons",
    "BasePaginator"
)


class PaginatorButtons(discord.ui.View):

    def __init__(self, *, paginator: BasePaginator) -> None:
        super().__init__(timeout=paginator.timeout)

        self.paginator: BasePaginator = paginator

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user is not None and interaction.user.id in {*values.OWNER_IDS, self.paginator.ctx.author.id}

    async def on_timeout(self) -> None:
        self.stop()
        await self.paginator.stop()

    async def on_error(self, error: Exception, item: discord.ui.Item[PaginatorButtons], interaction: discord.Interaction) -> None:
        return

    # Buttons

    @discord.ui.button(emoji=values.FIRST)
    async def first(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page == 0:
            return

        await self.paginator.change_page(page=0)

    @discord.ui.button(emoji=values.BACKWARD)
    async def backward(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page == 0:
            return

        await self.paginator.change_page(page=self.paginator.page - 1)

    @discord.ui.button()
    async def page_label(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:
        await interaction.response.defer()

    @discord.ui.button(emoji=values.FORWARD)
    async def forward(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page == len(self.paginator.pages) - 1:
            return

        await self.paginator.change_page(page=self.paginator.page + 1)

    @discord.ui.button(emoji=values.LAST)
    async def last(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page == len(self.paginator.pages) - 1:
            return

        await self.paginator.change_page(page=len(self.paginator.pages) - 1)

    @discord.ui.button(emoji=values.STOP)
    async def _stop(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        self.stop()
        await self.paginator.stop()


class BasePaginator(abc.ABC):

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
        join_pages: bool = True,
    ) -> None:

        self.ctx: custom.Context = ctx
        self.entries: list[Any] = entries
        self.per_page: int = per_page
        self.timeout: int = timeout
        self.edit_message: bool = edit_message
        self.delete_message: bool = delete_message
        self.codeblock: bool = codeblock
        self.splitter: str = splitter
        self.join_pages: bool = join_pages

        self.message: discord.Message | None = None
        self.view: PaginatorButtons = PaginatorButtons(paginator=self)

        self.page: int = 0

        if self.per_page > 1:
            self.pages: list[Any] = [
                self.splitter.join(self.entries[page:page + self.per_page]) if self.join_pages else self.entries[page:page + self.per_page]
                for page in range(0, len(self.entries), self.per_page)
            ]
        else:
            self.pages: list[Any] = self.entries

        self.CODEBLOCK_START: str = values.CODEBLOCK_START if self.codeblock else ""
        self.CODEBLOCK_END: str = values.CODEBLOCK_END if self.codeblock else ""

        self.embed: discord.Embed | None = None
        self.content: str | None = None

    @abc.abstractmethod
    async def set_page(self, page: int) -> None:
        raise NotImplementedError

    async def change_page(self, page: int) -> None:

        self.page = page
        self.view.page_label.label = f"{page + 1}/{len(self.pages)}"

        await self.set_page(self.page)

        if self.message:
            await self.message.edit(content=self.content, embed=self.embed, view=self.view)

    async def paginate(self) -> None:

        self.view.page_label.label = f"{self.page + 1}/{len(self.pages)}"

        await self.set_page(self.page)
        self.message = await self.ctx.reply(content=self.content, embed=self.embed, view=self.view)

    async def stop(self) -> None:

        if not self.message:
            return

        if self.delete_message:
            await self.message.delete()
        elif self.edit_message:
            await self.message.edit(content="*Message was deleted.*", embed=None, view=None)

        self.message = None
