# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    # Local
    from cd.bot import CD


__all__ = (
    "UserConfig",
)


class UserConfig:

    def __init__(self, bot: CD, data: dict[str, Any]) -> None:
        self.bot: CD = bot

        self.id: int = data["id"]

    def __repr__(self) -> str:
        return f"<UserConfig id={self.id}>"
