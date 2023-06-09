from typing import Any

from discord.ext import paginators


__all__ = ["Controller"]


class Controller(paginators.Controller):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.buttons["first"].emoji = "<:pf:959624334127800330>"
        self.buttons["previous"].emoji = "<:pp:959624365140492348>"
        self.buttons["next"].emoji = "<:pn:959624356558946325>"
        self.buttons["last"].emoji = "<:pl:959624322765447218>"
        self.buttons["stop"].emoji = "<:s:959624343246241913>"
