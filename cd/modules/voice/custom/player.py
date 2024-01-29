# Standard Library
from typing import TYPE_CHECKING

# Libraries
from discord.ext import lava


if TYPE_CHECKING:
    # Project
    from cd.bot import CD
    

class Player(lava.Player[CD]):
    pass