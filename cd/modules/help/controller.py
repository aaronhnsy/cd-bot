from __future__ import annotations

from typing import Self, TYPE_CHECKING, TypedDict

import discord
from discord.ext import paginators

if TYPE_CHECKING:
    from .paginator import HelpCommandPaginator


__all__ = ["HelpCommandController"]


class HelpCommandSelect(discord.ui.Select["HelpCommandController"]):

    async def callback(self, interaction: discord.Interaction) -> None:
        # noinspection PyUnresolvedReferences
        await interaction.response.defer()
        # set the paginators pages to the selected category
        assert self.view is not None
        fields = self.view.paginator.categories[self.values[0]].fields
        fields_per_page = self.view.paginator.items_per_page
        self.view.paginator.pages = [
            fields[chunk:chunk + fields_per_page]
            for chunk in range(0, len(fields), fields_per_page)
        ]
        # update the paginator embed title
        self.view.paginator.embeds[0].title = f"**{self.values[0]}**"
        # add/remove the controllers items based on the number of new pages
        self.view.set_item_visibilities()
        # go back to the first page
        await self.view.paginator.change_page(1)


class PaginatorControllerItems(TypedDict):
    select: HelpCommandSelect
    first: paginators.FirstPageButton[HelpCommandController]
    previous: paginators.PreviousPageButton[HelpCommandController]
    label: paginators.LabelButton[HelpCommandController]
    next: paginators.NextPageButton[HelpCommandController]
    last: paginators.LastPageButton[HelpCommandController]
    stop: paginators.StopButton[HelpCommandController]


class HelpCommandController(paginators.BaseController["HelpCommandPaginator"]):

    def __init__(self, paginator: HelpCommandPaginator) -> None:
        super().__init__(paginator)
        self.items: PaginatorControllerItems = {
            "select":   HelpCommandSelect(
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
            "first":    paginators.FirstPageButton[Self](emoji="<:pf:959624334127800330>"),
            "previous": paginators.PreviousPageButton[Self](emoji="<:pp:959624365140492348>"),
            "label":    paginators.LabelButton[Self](label="?"),
            "next":     paginators.NextPageButton[Self](emoji="<:pn:959624356558946325>"),
            "last":     paginators.LastPageButton[Self](emoji="<:pl:959624322765447218>"),
            "stop":     paginators.StopButton[Self](emoji="<:s:959624343246241913>")
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
