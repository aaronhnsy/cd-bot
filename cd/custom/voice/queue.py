# Future
from __future__ import annotations

# Standard Library
import asyncio
import collections
import random
from typing import Any

# Packages
import slate


__all__ = (
    "QueueItem",
    "Queue",
)


class QueueItem:

    def __init__(
        self,
        track: slate.Track, /,
        *,
        start_time: int = 0
    ) -> None:

        self.track: slate.Track = track
        self.start_time: int = start_time


class Queue:

    def __init__(self) -> None:

        self.items: list[QueueItem] = []
        self.history: list[slate.Track] = []

        self.loop_mode: slate.QueueLoopMode = slate.QueueLoopMode.DISABLED
        self.shuffle_state: bool = False

        self._waiters: collections.deque[asyncio.Future[Any]] = collections.deque()

        self._finished: asyncio.Event = asyncio.Event()
        self._finished.set()

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

    def reverse(self) -> None:
        self.items.reverse()

    def clear(self) -> None:
        self.items.clear()
        self.history.clear()

    def reset(
        self,
        *,
        clear: bool = True
    ) -> None:

        if clear:
            self.clear()

        for waiter in self._waiters:
            waiter.cancel()

        self._waiters.clear()

    def set_loop_mode(
        self,
        mode: slate.QueueLoopMode, /
    ) -> None:
        self.loop_mode = mode

    def set_shuffle_state(
        self,
        state: bool, /
    ) -> None:
        self.shuffle_state = state

    # Get

    def get(
        self,
        *,
        position: int = 0
    ) -> QueueItem | None:

        if len(self.items) >= 2 and self.shuffle_state:
            random.shuffle(self.items)

        try:
            item = self.items.pop(position)
        except IndexError:
            return None

        if self.loop_mode is not slate.QueueLoopMode.DISABLED:
            self.put(item, position=0 if self.loop_mode is slate.QueueLoopMode.CURRENT else None)

        return item

    async def get_wait(self) -> QueueItem:

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

        item = self.get(position=0)
        assert item is not None

        return item

    # Put

    def put(
        self,
        item: QueueItem, /,
        *,
        position: int | None = None
    ) -> None:

        if position is not None:
            self.items.insert(position, item)
        else:
            self.items.append(item)

        self._wakeup_next()

    def extend(
        self,
        items: list[QueueItem], /,
        *,
        position: int | None = None
    ) -> None:

        if position is not None:
            for index, item, in enumerate(items):
                self.items.insert(position + index, item)
        else:
            self.items.extend(items)

        self._wakeup_next()
