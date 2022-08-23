from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, TypedDict

import pendulum

from cd import utilities


if TYPE_CHECKING:
    from cd.bot import CD


__all__ = (
    "TodoData",
    "Todo",
)


class TodoData(TypedDict):
    id: int
    user_id: int
    created_at: datetime.datetime
    content: str
    jump_url: str


class Todo:

    def __init__(self, bot: CD, data: TodoData) -> None:
        self.bot: CD = bot

        self.id: int = data["id"]
        self.user_id: int = data["user_id"]
        self.created_at: pendulum.DateTime = utilities.convert_datetime(data["created_at"])
        self.content: str = data["content"]
        self.jump_url: str = data["jump_url"]

    def __repr__(self) -> str:
        return f"<Todo id={self.id}, user_id={self.user_id}, created_at={self.created_at}>"

    # Methods

    async def update_content(self, content: str, /, *, jump_url: str) -> None:
        data: TodoData = await self.bot.db.fetchrow(
            "UPDATE todos SET content = $1, jump_url = $2 WHERE id = $3 RETURNING *",
            content, jump_url, self.id,
        )
        self.content = data["content"]
        self.jump_url = data["jump_url"]
