from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from cd import utilities, values


if TYPE_CHECKING:
    from cd.paginators.base import BasePaginator


__all__ = (
    "PaginatorView",
)


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

    def __init__(
        self,
        *,
        paginator: BasePaginator
    ) -> None:

        super().__init__(
            timeout=paginator.timeout
        )

        self.paginator: BasePaginator = paginator

        self._first: FirstButton = FirstButton()
        self._previous: PreviousButton = PreviousButton()
        self._label: LabelButton = LabelButton()
        self._next: NextButton = NextButton()
        self._last: LastButton = LastButton()
        self._stop: StopButton = StopButton()

        length = len(self.paginator.pages)
        if length == 1:
            self.buttons = (
                self._stop,
            )
        elif length == 2:
            self.buttons = (
                self._previous,
                self._label,
                self._next,
                self._stop,
            )
        else:
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

    # Implemented ABC methods

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

    # Methods

    def update_state(self) -> None:

        self._label.label = f"{self.paginator.page + 1}/{len(self.paginator.pages)}"

        on_first = self.paginator.page == 0
        on_last = self.paginator.page == len(self.paginator.pages) - 1

        self._first.disabled = on_first
        self._previous.disabled = on_first

        self._next.disabled = on_last
        self._last.disabled = on_last
