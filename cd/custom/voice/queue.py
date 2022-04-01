# Future
from __future__ import annotations

# Standard Library
import asyncio
import collections
import random
from typing import Any

# Packages
import slate

# Local
from cd import custom


__all__ = (
    "Queue",
)


Track = slate.Track[custom.Context]


class Queue:

    def __init__(self) -> None:

        self.items: list[Track] = []
        self.history: list[Track] = []

        self.loop_mode: slate.QueueLoopMode = slate.QueueLoopMode.OFF

        self._finished: asyncio.Event = asyncio.Event()
        self._finished.set()
        self._waiters: collections.deque[asyncio.Future[Any]] = collections.deque()

    def __repr__(self) -> str:
        return f"<slate.Queue length={len(self.items)}>"

    def __len__(self) -> int:
        return self.items.__len__()

    def _wakeup_next(self) -> None:

        while self._waiters:

            if not (waiter := self._waiters.popleft()).done():
                waiter.set_result(None)
                break

    # Utilities

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def set_loop_mode(self, mode: slate.QueueLoopMode, /) -> None:
        self.loop_mode = mode

    def shuffle(self) -> None:
        random.shuffle(self.items)

    def reverse(self) -> None:
        self.items.reverse()

    def clear(self) -> None:
        self.items.clear()
        self.history.clear()

    def reset(self) -> None:

        self.clear()

        for waiter in self._waiters:
            waiter.cancel()

        self._waiters.clear()

    # Get / Put

    def get(self, position: int = 0) -> Track | None:

        try:
            item = self.items.pop(position)
        except IndexError:
            return None

        if self.loop_mode is not slate.QueueLoopMode.OFF:
            self.put(item, position=0 if self.loop_mode is slate.QueueLoopMode.CURRENT else None)

        return item

    async def get_wait(self) -> Track:

        while self.is_empty():

            loop = asyncio.get_event_loop()
            waiter = loop.create_future()

            self._waiters.append(waiter)

            try:
                await waiter

            except Exception:

                waiter.cancel()

                try:
                    self._waiters.remove(waiter)
                except ValueError:
                    pass

                if not self.is_empty() and not waiter.cancelled():
                    self._wakeup_next()

                raise

        item = self.items.pop()

        if self.loop_mode is not slate.QueueLoopMode.OFF:
            self.put(item, position=0 if self.loop_mode is slate.QueueLoopMode.CURRENT else None)

        return item

    def put(self, item: Track, position: int | None = None) -> None:

        if position is None:
            self.items.append(item)
        else:
            self.items.insert(position, item)

        self._wakeup_next()

    def extend(self, items: list[Track], position: int | None = None) -> None:

        if position is None:
            self.items.extend(items)
        else:
            for index, track, in enumerate(items):
                self.items.insert(position + index, track)

        self._wakeup_next()
