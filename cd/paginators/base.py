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
        await self.view.paginator.change_page(page=0)


class PreviousButton(discord.ui.Button["PaginatorView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PAGINATOR_PREVIOUS,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None

        await interaction.response.defer()
        await self.view.paginator.change_page(page=self.view.paginator.page - 1)


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
        await self.view.paginator.change_page(page=self.view.paginator.page + 1)


class LastButton(discord.ui.Button["PaginatorView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PAGINATOR_LAST,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None

        await interaction.response.defer()
        await self.view.paginator.change_page(page=len(self.view.paginator.pages) - 1)


class StopButton(discord.ui.Button["PaginatorView"]):

    def __init__(self) -> None:
        super().__init__(
            emoji=values.PAGINATOR_STOP,
            row=1
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        self.view.stop()
        await self.view.paginator.stop()


class PaginatorView(discord.ui.View):

    def __init__(self, *, paginator: BasePaginator) -> None:
        super().__init__(timeout=paginator.timeout)

        self.paginator: BasePaginator = paginator

        self._first: FirstButton = FirstButton()
        self._previous: PreviousButton = PreviousButton()
        self._label: LabelButton = LabelButton()
        self._next: NextButton = NextButton()
        self._last: LastButton = LastButton()
        self._stop: StopButton = StopButton()

        match len(self.paginator.pages):
            case 1:
                self.buttons = (
                    self._stop,
                )
            case 2:
                self.buttons = (
                    self._previous,
                    self._label,
                    self._next,
                    self._stop,
                )
            case _:
                self.buttons = (
                    self._first,
                    self._previous,
                    self._label,
                    self._next,
                    self._last,
                    self._stop,
                )

        for button in self.buttons:
            self.add_item(button)

    # Overrides

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if interaction.user and interaction.user.id in {self.paginator.ctx.author.id, *values.OWNER_IDS}:
            return True

        await interaction.response.send_message(
            embed=utilities.embed(
                colour=values.RED,
                description="You are not allowed to use this paginator."
            ),
            ephemeral=True
        )
        return False

    async def on_timeout(self) -> None:
        await self.paginator.stop()
        self.stop()

    # Custom methods

    def update_state(self) -> None:

        self._label.label = f"{self.paginator.page + 1}/{len(self.paginator.pages)}"

        if self.paginator.page == 0:
            self._first.disabled, self._previous.disabled = True, True
        else:
            self._first.disabled, self._previous.disabled = False, False

        if self.paginator.page == len(self.paginator.pages) - 1:
            self._next.disabled, self._last.disabled = True, True
        else:
            self._next.disabled, self._last.disabled = False, False


class BasePaginator(abc.ABC):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        entries: list[Any],
        per_page: int,
        start_page: int = 0,
        timeout: int = 300,
        edit_message: bool = False,
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

    # Private Methods

    @abc.abstractmethod
    async def _update_state(self) -> None:
        raise NotImplementedError

    # Public Methods

    async def change_page(self, page: int) -> None:

        self.page = page

        await self._update_state()
        self.view.update_state()

        if self.message:
            try:
                await self.message.edit(content=self.content, embed=self.embed, view=self.view)
            except (discord.NotFound, discord.HTTPException):
                pass

    async def start(self) -> None:

        self.view = PaginatorView(paginator=self)

        await self.change_page(page=self.page)
        self.message = await self.ctx.reply(content=self.content, embed=self.embed, view=self.view)

    async def stop(self) -> None:

        if not self.message:
            return

        try:
            if self.delete_message:
                await self.message.delete()

            elif self.edit_message:
                await self.message.edit(content="*Message was deleted.*", embed=None, view=None)

            else:
                for button in self.view.buttons:
                    button.disabled = True
                await self.message.edit(view=self.view)

        except (discord.NotFound, discord.HTTPException):
            pass

        self.message = None
