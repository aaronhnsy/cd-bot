# Future
from __future__ import annotations

# Standard Library
import abc
from typing import Any

# Packages
import discord

# My stuff
from core import values
from utilities import custom, slash


__all__ = (
    "PaginatorButtons",
    "BasePaginator"
)


class PaginatorButtons(discord.ui.View):

    def __init__(self, paginator: BasePaginator) -> None:
        super().__init__(timeout=paginator.timeout)

        self.paginator: BasePaginator = paginator

    # ABC Methods

    async def on_error(self, error: Exception, item: discord.ui.Item[PaginatorButtons], interaction: discord.Interaction) -> None:
        return

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user is not None and interaction.user.id in {*values.OWNER_IDS, self.paginator.ctx.author.id}

    async def on_timeout(self) -> None:
        self.stop()
        await self.paginator.stop()

    # Buttons

    @discord.ui.button(emoji=values.FIRST)
    async def _first(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        await self.paginator._change_page(page=0)

    @discord.ui.button(emoji=values.BACKWARD)
    async def _backward(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        await self.paginator._change_page(page=self.paginator.page - 1)

    @discord.ui.button()
    async def _label(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:
        await interaction.response.defer()

    @discord.ui.button(emoji=values.FORWARD)
    async def _forward(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        await self.paginator._change_page(page=self.paginator.page + 1)

    @discord.ui.button(emoji=values.LAST)
    async def _last(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        await self.paginator._change_page(page=len(self.paginator.pages) - 1)

    @discord.ui.button(emoji=values.STOP)
    async def _stop(self, _: discord.ui.Button[PaginatorButtons], interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        self.stop()
        await self.paginator.stop()


class BasePaginator(abc.ABC):

    def __init__(
        self,
        *,
        ctx: custom.Context | slash.ApplicationContext,
        entries: list[Any],
        per_page: int,
        start_page: int = 0,
        timeout: int = 300,
        edit_message: bool = True,
        delete_message: bool = False,
        codeblock: bool = False,
        splitter: str = "\n",
        join_pages: bool = True,
    ) -> None:

        self.ctx: custom.Context | slash.ApplicationContext = ctx
        self.entries: list[Any] = entries
        self.per_page: int = per_page
        self.start_page: int = start_page
        self.timeout: int = timeout
        self.edit_message: bool = edit_message
        self.delete_message: bool = delete_message
        self.codeblock: bool = codeblock
        self.splitter: str = splitter
        self.join_pages: bool = join_pages

        self.view: PaginatorButtons = PaginatorButtons(paginator=self)
        self.message: discord.Message | None = None
        self.embed: discord.Embed | None = None
        self.content: str | None = None

        self.page: int = start_page

        if self.per_page > 1:
            self.pages: list[Any] = [
                self.splitter.join(self.entries[page:page + self.per_page]) if self.join_pages else self.entries[page:page + self.per_page]
                for page in range(0, len(self.entries), self.per_page)
            ]
        else:
            self.pages: list[Any] = self.entries

        self.CODEBLOCK_START: str = values.CODEBLOCK_START if self.codeblock else ""
        self.CODEBLOCK_END: str = values.CODEBLOCK_END if self.codeblock else ""

    #

    @abc.abstractmethod
    async def _update_page(self) -> None:
        raise NotImplementedError

    def _update_buttons(self) -> None:

        self.view._label.label = f"{self.page + 1}/{len(self.pages)}"

        if self.page == 0:
            self.view._first.disabled, self.view._backward.disabled = True, True
        else:
            self.view._first.disabled, self.view._backward.disabled = False, False
        if self.page == len(self.pages) - 1:
            self.view._forward.disabled, self.view._last.disabled = True, True
        else:
            self.view._forward.disabled, self.view._last.disabled = False, False

    async def _change_page(self, page: int) -> None:

        self.page = page

        await self._update_page()
        self._update_buttons()

        if self.message:
            await self.message.edit(content=self.content, embed=self.embed, view=self.view)

    #

    async def start(self) -> None:

        await self._change_page(page=self.page)
        self.message = await self.ctx.reply(content=self.content, embed=self.embed, view=self.view)

    async def stop(self) -> None:

        if not self.message:
            return

        if self.delete_message:
            await self.message.delete()
        elif self.edit_message:
            await self.message.edit(content="*Message was deleted.*", embed=None, view=None)

        self.message = None
