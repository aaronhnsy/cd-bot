# Future
from __future__ import annotations

# Packages
import slate


__all__ = (
    "Queue",
)


class Queue(slate.Queue[slate.Track]):

    def __init__(self) -> None:
        super().__init__()

        self._shuffle_state: bool = False

    # Shuffle state

    @property
    def shuffle_state(self) -> bool:
        return self._shuffle_state

    def set_shuffle_state(self, state: bool, /) -> None:
        self._shuffle_state = state

    # Misc

    def is_history_empty(self) -> bool:
        return self._history.__len__() == 0

    # Overrides

    def _get(
        self,
        *,
        position: int,
        put_into_history: bool
    ) -> slate.Track:

        if len(self) >= 2 and self.shuffle_state:
            self.shuffle()

        return super()._get(position=position, put_into_history=put_into_history)
