# Future
from __future__ import annotations


__all__ = (
    "Time",
)


class Time:

    def __init__(self, seconds: int) -> None:
        self._seconds: int = seconds

    @property
    def seconds(self) -> int:
        return self._seconds
