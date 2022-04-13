# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, TypedDict

# Local
from cd import objects


if TYPE_CHECKING:
    # Local
    from cd.bot import CD


__all__ = (
    "UserData",
    "UserConfig",
)


class UserData(TypedDict):
    id: int


class UserConfig:

    def __init__(self, bot: CD, data: UserData) -> None:
        self.bot: CD = bot

        self.id: int = data["id"]
        self.todos: dict[int, objects.Todo] = {}

    def __repr__(self) -> str:
        return f"<UserConfig id={self.id}>"

    # Todos

    async def create_todo(self, content: str, /, *, jump_url: str) -> objects.Todo:

        data = await self.bot.db.fetchrow(
            "INSERT INTO todos (user_id, content, jump_url) VALUES ($1, $2, $3) RETURNING *",
            self.id, content, jump_url
        )

        todo = objects.Todo(self.bot, data=data)
        self.todos[todo.id] = todo

        return todo

    def get_todo(self, _id: int, /) -> objects.Todo | None:
        return self.todos.get(_id)

    async def delete_todo(self, _id: int, /) -> None:

        if self.todos.get(_id) is None:
            return

        await self.bot.db.execute(
            "DELETE FROM todos WHERE id = $1",
            _id
        )
        del self.todos[_id]
