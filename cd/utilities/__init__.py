from __future__ import annotations

from .asset import *
from .colours import *
from .datetime import *
from .embed import *
from .images import *
from .levels import *
from .logging import *
from .missing import *
from .upload import *


def readable_bool(value: bool) -> str:
    return str(value).replace("True", "yes").replace("False", "no")


def codeblock(content: str, language: str = "py", max_characters: int | None = None) -> str:

    if max_characters and len(content) > max_characters:
        return content

    return f"```{language}\n" \
           f"{content}" \
           f"\n```"


def truncate(text: str | int, characters: int) -> str:
    text = str(text)
    return text if len(text) < characters else f"{text[:characters]}..."


def pluralize(text: str, count: int) -> str:
    return f"{text}{'s' if count > 1 else ''}"


def guild_url(guild_id: int) -> str:
    return f"https://discord.com/channels/{guild_id}"


def user_url(user_id: int) -> str:
    return f"https://discord.com/users/{user_id}"
