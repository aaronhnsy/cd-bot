# Future
from __future__ import annotations

# My stuff
from utilities.objects.guild import *
from utilities.objects.user import *


class FakeTimeConverter:

    def __init__(self, seconds: int) -> None:
        self.seconds: int = seconds


class FakePrefixConverter:

    def __init__(self, value: str) -> None:
        self.value: str = value


class FakeImage:

    def __init__(self, url: str) -> None:
        self.url: str = url
