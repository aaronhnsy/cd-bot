# Future
from __future__ import annotations

# My stuff
from cd.utilities.asset import *
from cd.utilities.datetime import *
from cd.utilities.embed import *
from cd.utilities.imaging import *
from cd.utilities.links import *
from cd.utilities.logger import *
from cd.utilities.missing import *
from cd.utilities.upload import *


def readable_bool(value: bool) -> str:
    return str(value).replace("True", "yes").replace("False", "no")


def codeblock(content: str, language: str = "py", max_characters: int | None = None) -> str:

    if max_characters and len(content) > max_characters:
        return content

    return f"```{language}\n" \
           f"{content}" \
           f"\n```"
