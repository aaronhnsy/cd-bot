# Libraries
from discord.ext import paginators

# Project
from cd import custom, utilities, values

# Local Folder
from .controller import HelpCommandController
from .types import HelpCommandCategories


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
            embed=utilities.embed(
                colour=values.THEME_COLOUR,
                title=f"**{initial_category}**",
                thumbnail=utilities.asset_url(ctx.bot.user.display_avatar)  # pyright: ignore - bot.user is not None
            )
        )
        # store the categories
        self.categories: HelpCommandCategories = categories
