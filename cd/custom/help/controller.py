from __future__ import annotations

from typing import TYPE_CHECKING, Self

import discord
from discord.ext import paginators

from cd import values


if TYPE_CHECKING:
    from .paginator import HelpCommandPaginator
    from .types import HelpCommandControllerItems


__all__ = ["HelpCommandController"]


class HelpCommandControllerSelect(discord.ui.Select["HelpCommandController"]):

    async def callback(self, interaction: discord.Interaction) -> None:
        # noinspection PyUnresolvedReferences
        await interaction.response.defer()
        # set the paginator pages to the selected category
        assert self.view is not None
        fields = self.view.paginator.categories[self.values[0]].fields
        fields_per_page = self.view.paginator.items_per_page
        self.view.paginator.pages = [
            fields[chunk:chunk + fields_per_page]
            for chunk in range(0, len(fields), fields_per_page)
        ]
        # update the paginator embed title
        self.view.paginator.embeds[0].title = f"**{self.values[0]}**"
        # add/remove the controller items based on the number of new pages
        self.view.set_item_visibilities()
        # go back to the first page
        await self.view.paginator.change_page(1)


class HelpCommandController(paginators.BaseController["HelpCommandPaginator"]):

    def __init__(self, paginator: HelpCommandPaginator) -> None:
        super().__init__(paginator)
        self.items: HelpCommandControllerItems = {
            "select":   HelpCommandControllerSelect(
                placeholder="Select a category:",
                options=[
                    discord.SelectOption(
                        label=category.name,
                        value=category.name,
                        description=category.description,
                        emoji=category.emoji
                    )
                    for category in paginator.categories.values()
                ],
            ),
            "first":    paginators.FirstPageButton[Self](emoji=values.PAGINATOR_FIRST_BUTTON_EMOJI),
            "previous": paginators.PreviousPageButton[Self](emoji=values.PAGINATOR_PREVIOUS_BUTTON_EMOJI),
            "label":    paginators.LabelButton[Self](label="?"),
            "next":     paginators.NextPageButton[Self](emoji=values.PAGINATOR_NEXT_BUTTON_EMOJI),
            "last":     paginators.LastPageButton[Self](emoji=values.PAGINATOR_LAST_BUTTON_EMOJI),
            "stop":     paginators.StopButton[Self](emoji=values.PAGINATOR_STOP_BUTTON_EMOJI),
        }
        self.set_item_visibilities()

    def update_item_states(self) -> None:
        self.items["label"].label = f"{self.paginator.page}/{len(self.paginator.pages)}"
        if "first" in self.items:
            self.items["first"].disabled = self.paginator.page <= 2
            self.items["last"].disabled = self.paginator.page >= len(self.paginator.pages) - 1
        if "previous" in self.items:
            self.items["previous"].disabled = self.paginator.page <= 1
            self.items["next"].disabled = self.paginator.page >= len(self.paginator.pages)

    def set_item_visibilities(self) -> None:
        self.clear_items()
        match len(self.paginator.pages):
            case 1:
                items = ["select", "label", "stop"]
            case 2:
                items = ["select", "previous", "label", "next", "stop"]
            case _:
                items = ["select", "first", "previous", "label", "next", "last", "stop"]
        for item in items:
            self.add_item(self.items[item])  # type: ignore
