# Libraries
from discord.ext import paginators


__all__ = ["PaginatorController"]


class PaginatorController(paginators.DefaultController[paginators.PaginatorT]):

    def __init__(self, paginator: paginators.PaginatorT) -> None:
        super().__init__(paginator)
        self.items["stop"].emoji = "<:s:959624343246241913>"
        if "first" in self.items:
            self.items["first"].emoji = "<:pf:959624334127800330>"
            self.items["last"].emoji = "<:pl:959624322765447218>"
        if "previous" in self.items:
            self.items["previous"].emoji = "<:pp:959624365140492348>"
            self.items["next"].emoji = "<:pn:959624356558946325>"
