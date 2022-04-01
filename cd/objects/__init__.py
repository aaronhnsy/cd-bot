# Future
from __future__ import annotations

# Local
from cd.objects.guild import *
from cd.objects.user import *


class ConvertedTime:

    def __init__(self, seconds: int, original: str) -> None:
        self.seconds: int = seconds
        self.original: str = original


class ConvertedPrefix:

    def __init__(self, value: str) -> None:
        self.value: str = value
