import discord
from discord.ext import paginators

from cd import custom, utilities, values
from .types import HelpCommandCategories
from .controller import HelpCommandController


__all__ = ["HelpCommandPaginator"]


class HelpCommandPaginator(paginators.EmbedFieldsPaginator[custom.Context, HelpCommandController]):

    def __init__(
        self,
        ctx: custom.Context,
        categories: HelpCommandCategories,
        initial_category: str | None = None
    ) -> None:
        # use the first category if no initial category is selected
        if initial_category is None:
            initial_category = [*categories.keys()][0]
        # initialise the paginator
        super().__init__(
            ctx=ctx,
            fields=categories[initial_category].fields,
            fields_per_page=7,
            controller=HelpCommandController,
            embed=discord.Embed(
                title=f"**{initial_category}**",
                colour=values.THEME_COLOUR,
            ).set_thumbnail(
                url=utilities.asset_url(ctx.bot.user.display_avatar)  # pyright: ignore - bot.user is not None
            ),
        )
        # store the categories
        self.categories: HelpCommandCategories = categories
