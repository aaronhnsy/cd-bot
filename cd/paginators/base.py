# Future
from __future__ import annotations

# Standard Library
import abc
from typing import Any

# Packages
import discord

# Local
from cd import custom, utilities, values


class FirstButton(discord.ui.Button["PaginatorView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PAGINATOR_FIRST,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None

        await interaction.response.defer()
        await self.view.paginator._change_page(page=0)


class PreviousButton(discord.ui.Button["PaginatorView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PAGINATOR_PREVIOUS,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None

        await interaction.response.defer()
        await self.view.paginator._change_page(page=self.view.paginator.page - 1)


class LabelButton(discord.ui.Button["PaginatorView"]):

    def __init__(self) -> None:
        super().__init__()

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()


class NextButton(discord.ui.Button["PaginatorView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PAGINATOR_NEXT,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None

        await interaction.response.defer()
        await self.view.paginator._change_page(page=self.view.paginator.page + 1)


class LastButton(discord.ui.Button["PaginatorView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PAGINATOR_LAST,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None

        await interaction.response.defer()
        await self.view.paginator._change_page(page=len(self.view.paginator.pages) - 1)


class StopButton(discord.ui.Button["PaginatorView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PAGINATOR_STOP,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None

        self.view.stop()
        await self.view.paginator.stop()


class PaginatorView(discord.ui.View):

    def __init__(self, paginator: BasePaginator) -> None:
        super().__init__(timeout=paginator.timeout)

        self.paginator: BasePaginator = paginator

        self._first_button: FirstButton = FirstButton()
        self._previous_button: PreviousButton = PreviousButton()
        self._label_button: LabelButton = LabelButton()
        self._next_button: NextButton = NextButton()
        self._last_button: LastButton = LastButton()
        self._stop_button: StopButton = StopButton()

        match len(self.paginator.pages):
            case 1:
                buttons = (
                    self._stop_button,
                )
            case 2:
                self._stop_button.row = 1
                buttons = (
                    self._previous_button,
                    self._label_button,
                    self._next_button,
                    self._stop_button,
                )
            case _:
                buttons = (
                    self._first_button,
                    self._previous_button,
                    self._label_button,
                    self._next_button,
                    self._last_button,
                    self._stop_button,
                )

        for button in buttons:
            self.add_item(button)

        self._buttons = buttons

    # ABC Methods

    async def on_error(self, error: Exception, item: discord.ui.Item[PaginatorView], interaction: discord.Interaction) -> None:
        return

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user is not None and interaction.user.id in {*values.OWNER_IDS, self.paginator.ctx.author.id}

    async def on_timeout(self) -> None:
        self.stop()
        await self.paginator.stop()


class BasePaginator(abc.ABC):

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
        join_pages: bool = True,
    ) -> None:

        self.ctx: custom.Context = ctx
        self.entries: list[Any] = entries
        self.per_page: int = per_page
        self.start_page: int = start_page
        self.timeout: int = timeout
        self.edit_message: bool = edit_message
        self.delete_message: bool = delete_message
        self.codeblock: bool = codeblock
        self.splitter: str = splitter
        self.join_pages: bool = join_pages

        self.view: PaginatorView = utilities.MISSING
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

        self.view._label_button.label = f"{self.page + 1}/{len(self.pages)}"

        if self.page == 0:
            self.view._first_button.disabled, self.view._previous_button.disabled = True, True
        else:
            self.view._first_button.disabled, self.view._previous_button.disabled = False, False
        if self.page == len(self.pages) - 1:
            self.view._next_button.disabled, self.view._last_button.disabled = True, True
        else:
            self.view._next_button.disabled, self.view._last_button.disabled = False, False

    async def _change_page(self, page: int) -> None:

        self.page = page

        await self._update_page()
        self._update_buttons()

        if self.message:
            await self.message.edit(content=self.content, embed=self.embed, view=self.view)

    #

    async def start(self) -> None:

        self.view = PaginatorView(paginator=self)

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
