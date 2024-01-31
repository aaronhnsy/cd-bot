from discord.ext import paginators

from cd import values


__all__ = ["PaginatorController"]


class PaginatorController(paginators.DefaultController[paginators.PaginatorT]):

    def __init__(self, paginator: paginators.PaginatorT) -> None:
        super().__init__(paginator)
        self.items["stop"].emoji = values.PAGINATOR_STOP_BUTTON_EMOJI
        if "first" in self.items:
            self.items["first"].emoji = values.PAGINATOR_FIRST_BUTTON_EMOJI
            self.items["last"].emoji = values.PAGINATOR_LAST_BUTTON_EMOJI
        if "previous" in self.items:
            self.items["previous"].emoji = values.PAGINATOR_PREVIOUS_BUTTON_EMOJI
            self.items["next"].emoji = values.PAGINATOR_NEXT_BUTTON_EMOJI
